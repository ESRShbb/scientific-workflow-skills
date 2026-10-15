"""Inventory or copy sources without native Illustrator operations."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, stat

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''): h.update(part)
    return h.hexdigest()

def no_links(path):
    for p in (path.absolute(), *path.absolute().parents):
        if p.exists() or p.is_symlink():
            if p.is_symlink() or getattr(p.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
                raise ValueError('linked/reparse paths unsupported')

def run(paths, output=None):
    if not paths: raise ValueError('sources required')
    sources, rows = [], []
    for path in paths:
        path = Path(path); no_links(path); path = path.resolve()
        if not path.is_file(): raise ValueError('source is not a file')
        sources.append(path)
        rows.append({'source': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size})
    if output is not None:
        output = Path(output); no_links(output); output = output.resolve()
        if output.exists() or any(output == p or output in p.parents for p in sources): raise ValueError('output exists or overlaps input')
        output.mkdir(parents=True)
        for i, (source, row) in enumerate(zip(sources, rows), 1):
            target = output / f'{i:03d}_{source.name}'
            shutil.copy2(source, target)
            if os.path.samefile(source, target) or digest(target) != row['sha256'] or digest(source) != row['sha256']:
                raise ValueError('independent copy verification failed')
            row.update(copy=str(target), independent_copy=True)
        (output / 'manifest.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'source_records': rows, 'native_validation': 'NOT_PERFORMED'}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sources', nargs='+', type=Path); p.add_argument('--output', type=Path)
    args = p.parse_args(); print(json.dumps(run(args.sources, args.output), ensure_ascii=False, indent=2))
