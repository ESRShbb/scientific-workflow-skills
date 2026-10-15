"""Inventory Office OLE relationships; signatures do not certify native editability."""
from pathlib import Path
import argparse, hashlib, json, posixpath, zipfile
import xml.etree.ElementTree as ET

def local(tag): return tag.split('}')[-1]
def inspect(path):
    path = Path(path)
    if path.suffix.lower() not in {'.docx','.pptx'}: raise ValueError('DOCX/PPTX only')
    prefix = 'word/' if path.suffix.lower() == '.docx' else 'ppt/'
    records, errors = [], []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)): raise ValueError('duplicate ZIP member')
        for name in names:
            if not name.startswith(prefix) or not name.endswith('.xml'): continue
            root = ET.fromstring(z.read(name))
            parents = {c:p for p in root.iter() for c in p}
            objects = [e for e in root.iter() if local(e.tag) in {'OLEObject','oleObj'}]
            if not objects: continue
            relpath = posixpath.join(posixpath.dirname(name), '_rels', posixpath.basename(name)+'.rels')
            rels = {r.get('Id'):r for r in ET.fromstring(z.read(relpath))} if relpath in names else {}
            for obj in objects:
                rid = obj.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                rec = {'part':name,'relationship_id':rid,'progid':obj.get('ProgID',obj.get('progId'))}
                container = parents.get(obj)
                geometry = []
                if container is not None:
                    # Word VML style and PPT transform sizes are display geometry, not chemistry.
                    for e in container.iter():
                        if local(e.tag) in {'shape','ext','off'}:
                            attrs = {k:v for k,v in e.attrib.items() if k in {'style','cx','cy','x','y'}}
                            if attrs: geometry.append({'type':local(e.tag),'attributes':attrs})
                rec['display_geometry'] = geometry
                rel = rels.get(rid)
                if rel is None:
                    errors.append(f'missing relationship: {name}:{rid}'); rec['status']='MISSING_RELATIONSHIP'
                elif rel.get('TargetMode') == 'External':
                    rec.update(status='EXTERNAL_LINK',target=rel.get('Target'))
                else:
                    target = rel.get('Target','')
                    target = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(name),target))
                    if target not in names:
                        errors.append('missing embedding: '+target); rec.update(status='MISSING_EMBEDDING',target=target)
                    else:
                        data=z.read(target); rec.update(status='EMBEDDING_PRESENT',target=target,bytes=len(data),
                            sha256=hashlib.sha256(data).hexdigest(),contains_cdx_signature=b'VjCD0100' in data)
                records.append(rec)
    return {'relationship_integrity':'FAIL' if errors else 'PASS','errors':errors,'objects':records,
            'native_editability':'NOT_VERIFIED','scientific_identity':'NOT_VERIFIED'}

def compare(before, after, mapping=None):
    def keyed(report): return {(r['part'],r['relationship_id']):r for r in report['objects']}
    a,b=keyed(before),keyed(after)
    changes=[];pairs=[]
    if mapping is not None:
        used_a,used_b=set(),set()
        for m in mapping['objects']:
            x,y=tuple(m['before']),tuple(m['after'])
            if x not in a or y not in b or x in used_a or y in used_b or not m.get('evidence'):
                raise ValueError('explicit one-to-one existing object mapping and evidence required')
            pairs.append((x,y));used_a.add(x);used_b.add(y)
    else:
        # Word may reassign IDs and embedding filenames on save. Bind only unique unchanged payloads.
        # Reused relationship IDs alone cannot establish that two objects correspond.
        for x,row in a.items():
            h=row.get('sha256')
            left=[k for k,v in a.items() if h and v.get('sha256')==h]
            right=[k for k,v in b.items() if h and v.get('sha256')==h]
            if len(left)==len(right)==1:pairs.append((x,right[0]))
    for x,y in pairs:
        fields=[k for k in ('relationship_id','progid','status','target','sha256','display_geometry') if a[x].get(k)!=b[y].get(k)]
        if fields:changes.append({'before_object':x,'after_object':y,'changed_fields':fields,'before':a[x],'after':b[y]})
    unmatched_a=sorted(set(a)-{x for x,y in pairs});unmatched_b=sorted(set(b)-{y for x,y in pairs})
    return {'same_relationship_snapshot':not changes and not unmatched_a and not unmatched_b,'changes':changes,
            'unmatched_before':unmatched_a,'unmatched_after':unmatched_b,
            'object_correspondence':'SUPPLIED_MAPPING' if mapping is not None else 'UNIQUE_PAYLOADS_ONLY',
            'geometry_available_for_all':bool(a) and all(r.get('display_geometry') for r in list(a.values())+list(b.values())),
            'chemical_equivalence':'NOT_PROVEN','rendering':'NOT_VERIFIED'}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('office_file',type=Path);p.add_argument('--compare',type=Path);p.add_argument('--mapping',type=Path);a=p.parse_args()
    report=inspect(a.office_file)
    if a.mapping and not a.compare:raise ValueError('--mapping requires --compare')
    if a.compare:
        mapping=json.loads(a.mapping.read_text(encoding='utf-8-sig')) if a.mapping else None
        report['comparison']=compare(inspect(a.compare),report,mapping)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['relationship_integrity']=='PASS' else 2)
