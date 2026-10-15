"""Check export evidence, not chemical correctness or visual completeness."""
from pathlib import Path
import argparse
import json
import struct
import zlib
from raw_source_adapter import sha256_file


def png_dimensions(path):
    data = path.read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('not a PNG')
    offset, dimensions, has_idat, ended = 8, None, False, False
    while offset + 12 <= len(data):
        size = struct.unpack('>I', data[offset:offset+4])[0]
        kind = data[offset+4:offset+8]
        end = offset + 12 + size
        if end > len(data):
            raise ValueError('truncated PNG')
        payload = data[offset+8:offset+8+size]
        crc = struct.unpack('>I', data[offset+8+size:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('PNG CRC mismatch')
        if offset == 8 and (kind != b'IHDR' or size != 13):
            raise ValueError('missing PNG header')
        if kind == b'IHDR':
            dimensions = struct.unpack('>II', payload[:8])
        if kind == b'IDAT':
            has_idat = True
        offset = end
        if kind == b'IEND':
            ended = True
            break
    if not dimensions or min(dimensions) < 1 or not has_idat or not ended or offset != len(data):
        raise ValueError('incomplete PNG')
    return dimensions


def verify(root: Path):
    root = root.resolve()
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8-sig'))
    process_exit = 'UNVERIFIED'
    if (root / 'attempt.json').exists():
        attempt = json.loads((root / 'attempt.json').read_text(encoding='utf-8-sig'))
        if attempt.get('job_id') != manifest['job_id']:
            raise ValueError('native attempt belongs to another job')
        if (attempt.get('process_exited') is True and attempt.get('exit_code') == 0
                and attempt.get('state') == 'EXITED_UNVERIFIED'):
            process_exit = 'PASS'
        else:
            process_exit = 'CLEANUP_PENDING' if attempt.get('process_exited') is not True else 'FAILED'
    for p in (manifest['source'], manifest['working_copy']):
        if sha256_file(Path(p)) != manifest['source_sha256']:
            raise ValueError('input hash mismatch')
    report = json.loads((root / 'native_report.json').read_text(encoding='utf-8-sig'))
    if report.get('job_id') != manifest['job_id'] or report.get('saved_mnova') is not False:
        raise ValueError('wrong job or save state')
    if Path(report.get('source', '')).resolve() != Path(manifest['working_copy']).resolve() or report.get('source_sha256') != manifest['source_sha256']:
        raise ValueError('report source mismatch')
    if (root / 'success.txt').read_text(encoding='utf-8-sig').strip() != 'SUCCESS':
        raise ValueError('missing success evidence')
    log = (root / 'native.log').read_text(encoding='utf-8-sig')
    if 'ERROR' in log or 'SUCCESS' not in log:
        raise ValueError('native log failure')
    pages = report.get('pages', [])
    if not pages or report.get('page_count') != len(pages):
        raise ValueError('invalid page count')
    images = []
    for index, page in enumerate(pages, 1):
        path = Path(page['png']).resolve()
        expected = root / f'page_p{index}.png'
        if path != expected or page.get('page_number') != index or page.get('export_method') != 'Page.toPixmap(300)':
            raise ValueError('page mapping mismatch')
        dimensions = png_dimensions(path)
        images.append({'page': index, 'sha256': sha256_file(path), 'dimensions': dimensions})
    return {'technical_evidence': 'PASS', 'process_exit': process_exit,
            'overall': 'NEEDS_VISUAL_REVIEW' if process_exit in {'PASS','UNVERIFIED'} else 'EXPORT_VERIFIED_EXECUTION_INCOMPLETE',
            'scientific_review': 'NOT_PERFORMED', 'images': images}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job_directory', type=Path)
    parser.add_argument('--record', action='store_true', help='Update this job manifest after verified runner exit; never marks visual/scientific acceptance')
    args = parser.parse_args()
    result = verify(args.job_directory)
    if args.record:
        if result['process_exit'] != 'PASS':
            raise ValueError('cannot record native completion without runner exit evidence')
        path = args.job_directory / 'manifest.json'
        manifest = json.loads(path.read_text(encoding='utf-8-sig'))
        manifest.update(native_execution='TECHNICAL_PASS', verification=result,
                        execution_detail='Technical evidence checked; visual review remains pending.')
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
