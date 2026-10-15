"""Windows ChemDraw COM save/reopen/export on a fresh copy. Requires pywin32 and explicit ProgID."""
from pathlib import Path
import argparse,hashlib,json,shutil

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def value(obj,name,missing):
    try:
        v=getattr(obj,name)
        if v is None: missing.append(name)
        return v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
    except Exception:
        missing.append(name);return None

def model(doc):
    missing=[];atoms=[];bonds=[]
    for i in range(1,doc.Atoms.Count+1):
        a=doc.Atoms.Item(i)
        row={n:value(a,n,missing) for n in ('ID','ElementNumber','Charge','Isotope','NumImplicitHydrogens','LabelText','Stereochemistry')}
        atoms.append(row)
    for i in range(1,doc.Bonds.Count+1):
        b=doc.Bonds.Item(i)
        row={n:value(b,n,missing) for n in ('ID','BondOrder','BondDisplay','Stereochemistry')}
        row.update(atom1_id=value(b.Atom1,'ID',missing),atom2_id=value(b.Atom2,'ID',missing));bonds.append(row)
    return dict(atoms=atoms,bonds=bonds,unavailable_properties=sorted(set(missing)),chemical_equivalence='NOT_PROVEN')

def export_type(app,extension):
    matches=[]
    for i in range(1,app.ExportDataTypes.Count+1):
        t=app.ExportDataTypes.Item(i)
        if str(t.Extension).lower().lstrip('.')==extension:matches.append(t)
    if extension=='png' and len(matches)>1:
        # Some installations expose legacy image/x-png alongside standard image/png.
        standard=[t for t in matches if str(t.MIME).lower()=='image/png']
        if len(standard)==1:matches=standard
    if len(matches)!=1:raise ValueError('export type missing or ambiguous: '+extension)
    return matches[0]

def run(source,output,progid):
    import win32com.client
    source,output=Path(source).resolve(),Path(output).resolve()
    if not source.is_file() or source.suffix.lower()!='.cdx':raise ValueError('existing CDX required')
    if output.exists() or source.is_relative_to(output):raise ValueError('fresh independent output required')
    output.mkdir(parents=True);work=output/'working.cdx';shutil.copy2(source,work)
    initial=digest(source);report=dict(source=str(source),source_sha256=initial,progid=progid,
        native_execution='RUNNING',visual_review='NOT_PERFORMED',scientific_review='NOT_PERFORMED')
    doc=None;app=None
    try:
        if digest(work)!=initial:raise ValueError('copy mismatch')
        app=win32com.client.Dispatch(progid)
        report['documents_before']=app.Documents.Count
        # Open only the new work path, never use active document or collection ordering.
        doc=app.Documents.Open(str(work));before=model(doc);report['before']=before
        doc.SaveAs(str(output/'master.cdx'));doc.Close(0);doc=None
        doc=app.Documents.Open(str(output/'master.cdx'));after=model(doc);report['after']=after
        report['available_model_snapshot_equal']=(before['atoms']==after['atoms'] and before['bonds']==after['bonds'])
        report['export_types']={}
        for ext in ('cdxml','png'):
            target=output/('reopened.'+ext);kind=export_type(app,ext)
            report['export_types'][ext]={'extension':str(kind.Extension),'mime':str(kind.MIME)}
            doc.SaveAs(str(target),kind)
            if not target.is_file() or not target.stat().st_size:raise ValueError('empty export '+ext)
        report['native_execution']='SAVE_REOPEN_EXPORTED'
    except Exception as e:
        report.update(native_execution='FAILED',error=f'{type(e).__name__}: {e}')
    finally:
        if doc is not None:
            try:doc.Close(0)
            except Exception as e:report['close_error']=str(e)
        if app is not None:report['documents_after']=app.Documents.Count
        report['source_unchanged']=digest(source)==initial
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--progid',required=True);a=p.parse_args()
    r=run(a.input,a.output,a.progid)
    print(json.dumps({k:v for k,v in r.items() if k not in {'before','after'}},ensure_ascii=False,indent=2))
    raise SystemExit(0 if r['native_execution']=='SAVE_REOPEN_EXPORTED' and r['source_unchanged'] and 'close_error' not in r else 2)
