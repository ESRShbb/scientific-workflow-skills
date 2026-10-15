"""Prepare Illustrator JSX with explicit dependency/export settings; does not launch Illustrator."""
from pathlib import Path
import argparse,hashlib,json,shutil

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare(source,output,strategy,assets=None,scale=100):
    source,output=Path(source).resolve(),Path(output).resolve()
    if not source.is_file() or source.suffix.lower()!='.ai':raise ValueError('existing AI required')
    if output.exists() or source.is_relative_to(output):raise ValueError('fresh independent output required')
    if strategy not in {'preserve','package','embed'} or not 0<scale<=2000:raise ValueError('invalid strategy or scale')
    entries=[]
    if assets:
        raw=json.loads(Path(assets).read_text(encoding='utf-8-sig'))['assets']
        for e in raw:
            p=Path(e['source']);p=p if p.is_absolute() else Path(assets).resolve().parent/p
            p=p.resolve()
            if type(e['placed_index']) is not int or e['placed_index']<0:raise ValueError('zero-based placed_index required')
            if not p.is_file() or sha(p)!=e['sha256']:raise ValueError('asset hash mismatch')
            entries.append(dict(placed_index=e['placed_index'],source=str(p),sha256=e['sha256']))
    if len({e['placed_index'] for e in entries})!=len(entries):raise ValueError('duplicate placed_index')
    if strategy=='preserve' and entries:raise ValueError('preserve does not relink; choose package or embed')
    initial=sha(source);output.mkdir(parents=True);work=output/'working.ai';shutil.copy2(source,work)
    if sha(work)!=initial:raise ValueError('copy mismatch')
    for i,e in enumerate(entries):
        folder=output/'assets';folder.mkdir(exist_ok=True)
        target=folder/f'{i+1:03d}_{Path(e["source"]).name}';shutil.copy2(e['source'],target)
        if sha(target)!=e['sha256']:raise ValueError('asset copy mismatch')
        e['copied']=target.as_posix()
    cfg=dict(work=work.as_posix(),root=output.as_posix(),strategy=strategy,assets=entries,scale=scale)
    helper=Path(__file__).with_name('inspect_current_document.jsx').read_text(encoding='utf-8').split('// ENTRYPOINT')[0]
    template=Path(__file__).with_name('roundtrip.jsx.in').read_text(encoding='utf-8')
    (output/'run.jsx').write_text(helper+'\n'+template.replace('__CONFIG__',json.dumps(cfg,ensure_ascii=True)),encoding='utf-8')
    manifest=dict(source=str(source),source_sha256=initial,working_copy=str(work),native_execution_at_preparation='NOT_RUN',
        strategy=strategy,assets=entries,icc_embedding=True,scale=scale,migration='NOT_VERIFIED')
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--strategy',choices=['preserve','package','embed'],required=True)
    p.add_argument('--assets',type=Path);p.add_argument('--scale',type=float,default=100);a=p.parse_args()
    print(json.dumps(prepare(a.input,a.output,a.strategy,a.assets,a.scale),ensure_ascii=False,indent=2))
