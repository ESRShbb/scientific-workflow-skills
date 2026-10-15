"""Read numeric XY PZFX data without inferring identity, dropping records or fitting."""
from pathlib import Path
import argparse, hashlib, json, math
import xml.etree.ElementTree as ET

def local(node): return node.tag.split('}')[-1]
def child(node, name): return next((n for n in node if local(n) == name), None)
def title(node):
    item = child(node, 'Title')
    return ''.join(item.itertext()).strip() if item is not None else ''

def columns(column):
    result = []
    for sub in column:
        if local(sub) != 'Subcolumn': continue
        cells = []
        for cell in sub:
            if local(cell) != 'd': continue
            raw = ''.join(cell.itertext()).strip()
            value = None
            if raw:
                try:
                    value = float(raw)
                    if not math.isfinite(value): value = None
                except ValueError: pass
            cells.append({'raw': raw, 'value': value, 'attributes': dict(cell.attrib),
                          'numeric_status': 'blank' if not raw else ('finite' if value is not None else 'unsupported')})
        result.append(cells)
    return result

def inventory(path):
    path = Path(path)
    data = path.read_bytes()
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('XML DTD/entities are unsupported')
    root = ET.fromstring(data)
    if local(root) != 'GraphPadPrismFile': raise ValueError('not a PZFX root')
    records, unsupported, seen = [], [], {}
    for index, table in enumerate((x for x in root.iter() if local(x) == 'Table'), 1):
        table_id = table.get('ID', str(index))
        xcol = child(table, 'XColumn')
        if xcol is None:
            unsupported.append({'table_id': table_id, 'title': title(table), 'reason': 'no supported XColumn'})
            continue
        xs = columns(xcol)
        if len(xs) != 1:
            unsupported.append({'table_id': table_id, 'title': title(table), 'reason': 'requires one numeric X subcolumn'})
            continue
        ycols = [e for e in table if local(e) == 'YColumn']
        if not ycols:
            unsupported.append({'table_id': table_id, 'reason': 'no YColumn'})
        for yi, y in enumerate(ycols, 1):
            ys = columns(y)
            record_id = f'T{index}:Y{yi}'
            payload = {'x': xs[0], 'y': ys}
            digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            issues = []
            if not ys: issues.append('no Y subcolumns')
            if not xs[0]: issues.append('empty X')
            if any(len(s) != len(xs[0]) for s in ys): issues.append('unequal row counts; no truncation applied')
            if any(c['numeric_status'] == 'unsupported' for s in [xs[0], *ys] for c in s): issues.append('unsupported numeric cells')
            if not title(y): issues.append('missing Y label; identity unresolved')
            records.append({'record_id': record_id, 'table_id': table_id, 'table_title': title(table),
                            'y_index': yi, 'y_title': title(y), 'table_attributes': dict(table.attrib),
                            **payload, 'content_sha256': digest, 'duplicate_of': seen.get(digest), 'issues': issues})
            seen.setdefault(digest, record_id)
    tables = {r['table_id'] for r in records}
    counts = {'supported_xy_tables': len(tables), 'y_columns': len(records),
              'y_subcolumns': sum(len(r['y']) for r in records),
              'y_data_cells': sum(len(s) for r in records for s in r['y']),
              'finite_y_cells': sum(c['numeric_status'] == 'finite' for r in records for s in r['y'] for c in s),
              'blank_y_cells': sum(c['numeric_status'] == 'blank' for r in records for s in r['y'] for c in s)}
    return {'source': str(path.resolve()), 'sha256': hashlib.sha256(data).hexdigest(), 'counts': counts,
            'status': 'EXTRACTED_ONLY', 'records': records, 'unsupported_tables': unsupported,
            'fitting': 'NOT_PERFORMED', 'compound_identity': 'NOT_VERIFIED'}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = inventory(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
