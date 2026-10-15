"""Preserve a labeled Prism text export. Empty/numeric-only tables are not parameter evidence."""
from pathlib import Path
import argparse,json,re,hashlib

def read(path, encoding, expected_title, title_file=None):
    data=Path(path).read_bytes();text=data.decode(encoding).lstrip('\ufeff')
    lines=text.splitlines()
    if title_file:
        title=Path(title_file).read_text(encoding=encoding).lstrip('\ufeff').strip()
        if title!=expected_title:raise ValueError('native result title mismatch')
        content=lines;start=1
    else:
        if not lines or lines[0].strip()!=expected_title: raise ValueError('native result title mismatch')
        title=lines[0];content=lines[1:];start=2
    rows=[]
    for i,line in enumerate(content,start):
        cells=line.split('\t'); label=cells[0].strip()
        if not label: continue
        if re.fullmatch(r'[+\-\d.,eE %]+',label): continue
        rows.append({'line':i,'label':label,'cells':cells[1:],'raw':line})
    if not rows: raise ValueError('no labeled rows; use verified native parameter mapping or native table export with labels')
    return dict(source=str(Path(path).resolve()),sha256=hashlib.sha256(data).hexdigest(),title=title,
                title_source=str(Path(title_file).resolve()) if title_file else str(Path(path).resolve()),
                rows=rows,status='LABELED_EXPORT_ONLY',label_provenance='CHECK_EXPORT_METHOD_AND_MAPPING',
                analysis_input='NOT_VERIFIED',units='NOT_INFERRED')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--encoding',required=True);p.add_argument('--expected-title',required=True)
    p.add_argument('--title-file',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=read(a.input,a.encoding,a.expected_title,a.title_file)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
