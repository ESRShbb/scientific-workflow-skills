"""CDXML XML integrity and conservative attribute snapshots, not chemical equivalence."""
from pathlib import Path
import argparse, hashlib, json
import xml.etree.ElementTree as ET

LAYOUT = {'p','BoundingBox','Head3D','Tail3D','Center3D','MajorAxisEnd3D','MinorAxisEnd3D',
          'WidthPages','HeightPages','PrintMargins','WindowPosition','WindowSize','Name','CreationProgram'}
OBJECTS = {'page','fragment','n','b','t','graphic','arrow','group'}

def snapshot(node):
    return [node.tag, sorted((k,v) for k,v in node.attrib.items() if k not in LAYOUT),
            (node.text or '').strip(), [snapshot(c) for c in node]]

def inspect(path):
    path = Path(path); data = path.read_bytes()
    if b'<!ENTITY' in data.upper(): raise ValueError('XML entities unsupported')
    root = ET.fromstring(data)
    if root.tag != 'CDXML': raise ValueError('CDXML root required')
    pages = root.findall('page'); errors, ids = [], set()
    if not pages: errors.append('no pages')
    for node in root.iter():
        if node.tag in OBJECTS and node.get('id'):
            ident = node.get('id')
            if ident in ids: errors.append('duplicate object id: ' + ident)
            ids.add(ident)
    for page in pages:
        nodes = {n.get('id') for n in page.iter('n') if n.get('id')}
        for b in page.iter('b'):
            if not b.get('B') or not b.get('E') or b.get('B') not in nodes or b.get('E') not in nodes:
                errors.append('unresolved bond endpoint: ' + str(b.get('id')))
            if b.get('B') == b.get('E'): errors.append('self bond: ' + str(b.get('id')))
    semantic = snapshot(root)
    return {'xml_integrity': 'FAIL' if errors else 'PASS', 'errors': errors,
            'file_sha256': hashlib.sha256(data).hexdigest(), 'pages': len(pages),
            'semantic_snapshot_sha256': hashlib.sha256(json.dumps(semantic, ensure_ascii=False).encode()).hexdigest(),
            'chemical_equivalence': 'NOT_PROVEN', 'native_open': 'NOT_PERFORMED'}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('cdxml', type=Path); p.add_argument('--compare', type=Path)
    args = p.parse_args(); result = inspect(args.cdxml)
    if args.compare:
        before = inspect(args.compare)
        result['baseline_xml_integrity'] = before['xml_integrity']
        result['semantic_snapshot_equal'] = result['semantic_snapshot_sha256'] == before['semantic_snapshot_sha256']
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['xml_integrity'] == 'PASS' and result.get('baseline_xml_integrity','PASS') == 'PASS' and result.get('semantic_snapshot_equal',True) else 2)
