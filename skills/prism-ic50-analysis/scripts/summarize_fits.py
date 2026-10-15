"""Summarize explicitly reviewed independent fit rows; never fit or decide QC."""
from pathlib import Path
import argparse, csv, json, math, statistics

def summarize(rows, method, min_n):
    if method not in {'arithmetic', 'log'} or type(min_n) is not int or min_n < 1:
        raise ValueError('explicit method and positive integer min_n required')
    groups, seen = {}, set()
    for row in rows:
        for key in ('sample_id', 'experiment_id', 'unit', 'decision'):
            if not row.get(key, '').strip(): raise ValueError(f'missing {key}')
        ident = (row['sample_id'], row['experiment_id'])
        if ident in seen: raise ValueError('duplicate independent experiment key')
        seen.add(ident)
        group = groups.setdefault(row['sample_id'], {'unit': row['unit'], 'included': [], 'excluded': []})
        if group['unit'] != row['unit']: raise ValueError('mixed units for sample')
        if row['decision'] == 'exclude':
            if not row.get('reason', '').strip(): raise ValueError('exclusion reason missing')
            group['excluded'].append(dict(row)); continue
        if row['decision'] != 'include': raise ValueError('decision must be include or exclude')
        value = float(row['ic50'])
        if not math.isfinite(value) or value <= 0: raise ValueError('included IC50 must be finite and positive')
        group['included'].append({**row, 'value': value})
    if not groups: raise ValueError('no data rows')
    for group in groups.values():
        vals = [r['value'] for r in group['included']]
        group.update(n=len(vals), method=method, min_n=min_n, summary=None)
        if len(vals) < min_n: continue
        if method == 'arithmetic':
            group['summary'] = {'arithmetic_mean': statistics.mean(vals),
                                'sample_sd': statistics.stdev(vals) if len(vals) > 1 else None}
        else:
            logs = [math.log10(v) for v in vals]
            sd = statistics.stdev(logs) if len(logs) > 1 else None
            group['summary'] = {'geometric_mean': 10 ** statistics.mean(logs),
                                'sd_log10': sd, 'geometric_sd_factor': 10 ** sd if sd is not None else None}
    return {'status': 'SUMMARY_OF_SUPPLIED_REVIEW_DECISIONS', 'independence_verified': False, 'samples': groups}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv', type=Path); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--method', choices=['arithmetic', 'log'], required=True); p.add_argument('--min-n', type=int, required=True)
    args = p.parse_args()
    with args.csv.open(encoding='utf-8-sig', newline='') as f: result = summarize(list(csv.DictReader(f)), args.method, args.min_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
