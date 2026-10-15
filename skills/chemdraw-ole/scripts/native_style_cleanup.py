"""Style and optionally clean a new ChemDraw copy using its native COM interface."""
from pathlib import Path
import argparse, json, math, statistics, xml.etree.ElementTree as ET
from native_roundtrip import digest, model, export_type

def geometry(path):
    root=ET.parse(path).getroot();nodes={n.get('id'):n for n in root.iter('n')};lengths=[]
    for b in root.iter('b'):
        a=nodes.get(b.get('B'));z=nodes.get(b.get('E'))
        if a is not None and z is not None and a.get('p') and z.get('p'):
            lengths.append(math.dist(list(map(float,a.get('p').split())),list(map(float,z.get('p').split()))))
    return dict(document_style={k:root.get(k) for k in ('LabelSize','CaptionSize','LineWidth','BoldWidth','BondLength')},
                text_sizes=sorted({s.get('size') for s in root.iter('s') if s.get('size')}),
                bonds=len(lengths),median_bond_length_pt=statistics.median(lengths) if lengths else None,
                longest_bond_pt=max(lengths) if lengths else None)

def run(source,output,progid,font_pt=10,line_cm=0.04,cleanup=False):
    import shutil,win32com.client
    source=Path(source).resolve();output=Path(output).resolve()
    if not source.is_file() or source.suffix.lower()!='.cdx':raise ValueError('existing CDX required')
    if output.exists() or source.is_relative_to(output):raise ValueError('fresh independent output required')
    if not 0<font_pt<200 or not 0<line_cm<1:raise ValueError('invalid style size')
    output.mkdir(parents=True);work=output/'working.cdx';shutil.copy2(source,work)
    original=digest(source);doc=None;report=dict(source=str(source),source_sha256=original,
        requested_font_pt=font_pt,requested_line_cm=line_cm,requested_line_pt=line_cm*72/2.54,
        cleanup_requested=cleanup,native_execution='RUNNING',visual_review='NOT_PERFORMED')
    try:
        app=win32com.client.Dispatch(progid);doc=app.Documents.Open(str(work))
        report['before_model']=model(doc)
        doc.SaveAs(str(output/'before.cdxml'),export_type(app,'cdxml'))
        report['before_geometry']=geometry(output/'before.cdxml')
        # Native defaults do not replace explicit text-run sizes in existing labels.
        tree=ET.parse(output/'before.cdxml');root=tree.getroot()
        for node in root.iter():
            for key,val in [('LabelSize',font_pt),('CaptionSize',font_pt),('LineWidth',line_cm*72/2.54)]:
                if node is root or key in node.attrib:node.set(key,f'{val:.6f}')
            if node.tag=='s':node.set('size',f'{font_pt:g}')
        styled=output/'styled.cdxml';tree.write(styled,encoding='utf-8',xml_declaration=True)
        doc.Close(0);doc=None;doc=app.Documents.Open(str(styled))
        if cleanup:doc.Objects.Clean(False)  # Native tidy; do not request de-novo depiction.
        doc.SaveAs(str(output/'master.cdx'));doc.Close(0);doc=None
        doc=app.Documents.Open(str(output/'master.cdx'));report['after_model']=model(doc)
        for ext in ('cdxml','png'):doc.SaveAs(str(output/('reopened.'+ext)),export_type(app,ext))
        report['after_geometry']=geometry(output/'reopened.cdxml')
        report['available_model_snapshot_equal']=report['before_model']==report['after_model']
        report['native_execution']='SAVE_REOPEN_EXPORTED'
    except Exception as e:report.update(native_execution='FAILED',error=f'{type(e).__name__}: {e}')
    finally:
        if doc is not None:
            try:doc.Close(0)
            except Exception as e:report['close_error']=str(e)
        report['source_unchanged']=digest(source)==original
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--progid',required=True);p.add_argument('--font-pt',type=float,default=10);p.add_argument('--line-cm',type=float,default=0.04)
    p.add_argument('--cleanup',action='store_true');a=p.parse_args()
    r=run(a.input,a.output,a.progid,a.font_pt,a.line_cm,a.cleanup)
    print(json.dumps({k:v for k,v in r.items() if 'model' not in k},ensure_ascii=False,indent=2))
    raise SystemExit(0 if r['native_execution']=='SAVE_REOPEN_EXPORTED' and r['source_unchanged'] and 'close_error' not in r else 2)
