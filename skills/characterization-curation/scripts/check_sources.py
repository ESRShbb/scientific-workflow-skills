"""Validate source-file declarations without making chemical decisions."""
from pathlib import Path
import argparse, hashlib, json

def check(manifest, base):
    rows = manifest.get('entries')
    if not isinstance(rows, list) or not rows: raise ValueError('nonempty entries required')
    results, seen, selections, hashes = [], set(), {}, {}
    for row in rows:
        for field in ('entry_id', 'sample_id', 'batch_id', 'modality', 'selection', 'status', 'reason'):
            if not isinstance(row.get(field), str) or not row[field].strip(): raise ValueError(f'missing {field}')
        if row['entry_id'] in seen: raise ValueError('duplicate entry_id')
        seen.add(row['entry_id'])
        if row['selection'] not in {'selected', 'candidate'}: raise ValueError('invalid selection')
        if row['status'] not in {'candidate', 'verified', 'missing', 'not_applicable', 'excluded', 'unusable'}: raise ValueError('invalid status')
        result = {**row, 'file_integrity': 'NOT_CHECKED'}
        if row['selection'] == 'selected':
            if row['status'] not in {'candidate', 'verified'}: raise ValueError('selected source has incompatible status')
            if not all(row.get(k) for k in ('source', 'sha256', 'locator')): raise ValueError('selected source requires path/hash/locator')
            selections.setdefault((row['sample_id'], row['batch_id'], row['modality']), []).append(row)
        if row.get('source'):
            path = (base / row['source']).resolve()
            if not path.is_file():
                result['file_integrity'] = 'MISSING'
            else:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                result.update(actual_sha256=digest, resolved_source=str(path),
                              file_integrity='PASS' if digest.lower() == str(row.get('sha256', '')).lower() else 'HASH_MISMATCH_OR_UNPINNED')
                hashes.setdefault(digest, []).append(row['entry_id'])
        results.append(result)
    conflicts = []
    for key, chosen in selections.items():
        if len(chosen) > 1 and (not chosen[0].get('selection_group') or len({r.get('selection_group') for r in chosen}) != 1):
            conflicts.append({'sample_batch_modality': key, 'entries': [r['entry_id'] for r in chosen]})
    failed = conflicts or any(r['file_integrity'] not in {'PASS', 'NOT_CHECKED'} for r in results)
    return {'technical_status': 'FAIL' if failed else 'PASS', 'scientific_review': 'NOT_PERFORMED',
            'entries': results, 'selection_conflicts': conflicts,
            'shared_file_candidates': [v for v in hashes.values() if len(v) > 1]}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    report = check(json.loads(args.manifest.read_text(encoding='utf-8-sig')), args.manifest.resolve().parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f: json.dump(report, f, ensure_ascii=False, indent=2)
    raise SystemExit(0 if report['technical_status'] == 'PASS' else 2)
