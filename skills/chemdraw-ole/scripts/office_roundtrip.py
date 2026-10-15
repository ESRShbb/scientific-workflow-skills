"""Word ChemDraw OLE audit/save/reopen on one new DOCX copy, Windows + pywin32.

Enumerates inline and floating objects; activates before reading OLEFormat.Object.
Close/reopen the owned container between objects, never infer ChemDraw document order.
"""
from pathlib import Path
import argparse, json, shutil
from native_roundtrip import model, digest

def shapes(doc):
    for kind, collection in [('inline',doc.InlineShapes),('floating',doc.Shapes)]:
        for index in range(1,collection.Count+1):
            sh=collection.Item(index)
            try:progid=str(sh.OLEFormat.ProgID)
            except Exception:continue
            if 'chemdraw' in progid.casefold():yield kind,index,progid

def geometry(sh,kind):
    row={'width_pt':float(sh.Width),'height_pt':float(sh.Height)}
    try:row['anchor_start']=int((sh.Range if kind=='inline' else sh.Anchor).Start)
    except Exception:row['anchor_start']=None
    return row

def select(doc,kind,index):
    return (doc.InlineShapes if kind=='inline' else doc.Shapes).Item(index)

def run(source,output,export_pdf=False):
    import win32com.client
    source,output=Path(source).resolve(),Path(output).resolve()
    if not source.is_file() or source.suffix.lower()!='.docx':raise ValueError('existing DOCX required')
    if output.exists() or source.is_relative_to(output):raise ValueError('fresh independent output required')
    output.mkdir(parents=True);work=output/'master.docx';shutil.copy2(source,work)
    baseline=digest(source);report={'source':str(source),'source_sha256':baseline,'master':str(work),
        'objects':[],'native_execution':'RUNNING','visual_review':'NOT_PERFORMED','scientific_review':'NOT_PERFORMED'}
    app=None;doc=None
    def owned_instance():
        a=win32com.client.DispatchEx('Word.Application');a.Visible=True;a.DisplayAlerts=0
        return a
    def read_one(kind,index,progid,save):
        a=owned_instance();d=None
        try:
            d=a.Documents.Open(str(work));sh=select(d,kind,index)
            if str(sh.OLEFormat.ProgID)!=progid:raise RuntimeError('Object locator changed')
            g=geometry(sh,kind);sh.OLEFormat.Activate();m=model(sh.OLEFormat.Object)
            if save:d.Save()
            return g,m
        finally:
            if d is not None:d.Close(0)
            a.Quit()
    try:
        app=owned_instance()
        doc=app.Documents.Open(str(work));locators=list(shapes(doc));doc.Close(0);doc=None
        app.Quit();app=None
        report['object_count']=len(locators)
        for kind,index,progid in locators:
            row={'kind':kind,'index':index,'progid':progid};report['objects'].append(row)
            try:
                row['before_geometry'],row['before_model']=read_one(kind,index,progid,True)
                row['after_geometry'],row['after_model']=read_one(kind,index,progid,False)
                row['editable_after_reopen']=True
                row['available_model_equal']=all(row['before_model'][k]==row['after_model'][k] for k in ('atoms','bonds'))
                row['geometry_equal']=row['before_geometry']==row['after_geometry']
                row['state']='READ_SAVE_REOPENED'
            except Exception as e:row.update(state='FAILED',error=f'{type(e).__name__}: {e}')
            finally:
                if doc is not None:doc.Close(0);doc=None
            (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print('OBJECT',kind,index,row['state'],flush=True)
        if export_pdf:
            app=owned_instance()
            doc=app.Documents.Open(str(work));doc.ExportAsFixedFormat(str(output/'reopened.pdf'),17)
            doc.Close(0);doc=None
        report['native_execution']='ROUNDTRIP_COMPLETE' if locators and all(r['state']=='READ_SAVE_REOPENED' for r in report['objects']) else 'PARTIAL'
    except Exception as e:report.update(native_execution='FAILED',error=f'{type(e).__name__}: {e}')
    finally:
        if doc is not None:
            try:doc.Close(0)
            except Exception as e:report['close_error']=str(e)
        if app is not None:
            # DispatchEx created this task-owned Word instance; not the user's session.
            try:app.Quit()
            except Exception as e:report['quit_error']=str(e)
        report['source_unchanged']=digest(source)==baseline
        report['master_sha256']=digest(work)
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--export-pdf',action='store_true');a=p.parse_args()
    r=run(a.input,a.output,a.export_pdf)
    print(json.dumps({k:v for k,v in r.items() if k!='objects'},ensure_ascii=False,indent=2))
    raise SystemExit(0 if r['native_execution']=='ROUNDTRIP_COMPLETE' and r['source_unchanged'] and not r.get('quit_error') and not r.get('close_error') else 2)
