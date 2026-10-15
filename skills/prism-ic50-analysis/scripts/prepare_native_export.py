"""Prepare labeled native results export from explicitly verified sheet identities; no fitting."""
from pathlib import Path
import argparse, hashlib, json, shutil

def prepare(source, sheet_map, output, encoding='utf-8', label_mode='mapped'):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file() or source.suffix.lower() != '.pzfx': raise ValueError('existing PZFX required')
    sheets = json.loads(Path(sheet_map).read_text(encoding='utf-8-sig'))['sheets']
    if label_mode not in {'mapped','native'}:raise ValueError('unknown label mode')
    seen = set()
    for s in sheets:
        n = s['number']
        if type(n) is not int or n < 1 or n in seen: raise ValueError('unique positive result-sheet numbers required')
        if s.get('verified') is not True or not s.get('expected_title') or not s.get('evidence'):
            raise ValueError('verify sheet identity in native project first; do not probe guessed indices')
        if label_mode=='native':
            seen.add(n)
            continue
        cols=s.get('columns',[]);params=s.get('parameters',[])
        if not cols or any(type(c) is not int or c<1 for c in cols) or len(set(cols))!=len(cols):
            raise ValueError('explicit unique result column numbers required')
        if cols!=list(range(cols[0],cols[-1]+1)):raise ValueError('columns must be an increasing contiguous range')
        if not params:raise ValueError('native-verified parameter row/label map required')
        for x in params:
            if (type(x.get('row')) is not int or x['row']<1 or not x.get('label')
                    or x.get('verified') is not True or not x.get('evidence')):
                raise ValueError('each parameter needs native-verified row, label and evidence')
            if any(c in x['label'] for c in ('"','\n','\r')):raise ValueError('unsupported parameter label')
        seen.add(n)
    if not sheets: raise ValueError('no verified sheets')
    if output.exists() or source.is_relative_to(output): raise ValueError('new independent output required')
    def quoted(p):
        v = str(p)
        if any(x in v for x in ('"', '\n', '\r')): raise ValueError('unsupported path')
        return '"'+v+'"'
    work = output/'working.pzfx'
    lines = ['/* Read-only export of existing results; no RecalcAll or fitting. */', 'Open '+quoted(work)]
    for s in sheets:
        if label_mode=='native':
            lines += ['GoTo R '+str(s['number']),
                      'OpenOutput '+quoted(output/f'title_R{s["number"]}.txt'),'WTitle','CloseOutput',
                      'ExportTable '+quoted(output/f'result_R{s["number"]}.txt')]
            continue
        lines += ['GoTo R '+str(s['number']), 'OpenOutput '+quoted(output/f'raw_R{s["number"]}.txt'),
                  'WTitle', 'WSheet 1, 1', 'CloseOutput',
                  'OpenOutput '+quoted(output/f'result_R{s["number"]}.txt'), 'WTitle']
        cols=str(s['columns'][0]) if len(s['columns'])==1 else f'{s["columns"][0]}-{s["columns"][-1]}'
        for x in s['parameters']:
            lines.append(f'WBlock {x["row"]}, {cols}, "{x["label"]}"')
        lines += ['CloseOutput']
    lines += ['Close', 'CloseScriptDialog']
    code = '\n'.join(lines)+'\n'
    encoded = code.encode(encoding)  # fail before writing if host encoding cannot express paths
    output.mkdir(parents=True)
    shutil.copy2(source, work)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if hashlib.sha256(work.read_bytes()).hexdigest()!=digest: raise ValueError('copy mismatch')
    (output/'export.pzc').write_bytes(encoded)
    manifest = dict(source=str(source), source_sha256=digest, working_copy=str(work), sheets=sheets,label_mode=label_mode,
                    command_encoding=encoding, native_execution_at_preparation='NOT_RUN', fitting='NOT_PERFORMED',
                    label_provenance='NATIVE_EXPORTTABLE' if label_mode=='native' else 'SUPPLIED_VERIFIED_MAP_NOT_AUTOMATIC_NATIVE_LABEL_DISCOVERY')
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('--sheets',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--encoding',default='utf-8')
    p.add_argument('--label-mode',choices=['mapped','native'],default='mapped')
    a=p.parse_args();print(json.dumps(prepare(a.input,a.sheets,a.output,a.encoding,a.label_mode),ensure_ascii=False,indent=2))
