"""Prepare a fresh, portable Mnova whole-page export job. Never launches Mnova."""
from pathlib import Path
import argparse
import json
import shutil
import uuid
from raw_source_adapter import sha256_file, validate_output, _check_path


def prepare(source: Path, output: Path, software: Path | None = None) -> dict:
    _check_path(source)
    source = source.resolve()
    if not source.is_file() or source.suffix.lower() != '.mnova':
        raise ValueError('input must be an existing .mnova file; native readability is not established here')
    if software is not None and not software.is_file():
        raise ValueError('specified software executable is missing')
    validate_output(output, [source])
    before = sha256_file(source)
    output.mkdir(parents=True)
    output = output.resolve()
    work = output / 'working.mnova'
    shutil.copy2(source, work)
    if before != sha256_file(work) or before != sha256_file(source):
        raise ValueError('copy verification failed')
    job_id = uuid.uuid4().hex
    function = 'qNmrExport' + job_id
    job = {'job_id': job_id, 'mnova': work.as_posix(), 'source_sha256': before,
           'export_dir': output.as_posix(), 'prefix': 'page',
           'report_out': (output / 'native_report.json').as_posix(),
           'success_marker': (output / 'success.txt').as_posix(),
           'log': (output / 'native.log').as_posix()}
    if any('\n' in v or '\r' in v for v in job.values()):
        raise ValueError('newline paths are unsupported')
    job_path = output / 'job.txt'
    job_path.write_text(''.join(f'{k}={v}\n' for k, v in job.items()), encoding='utf-8')
    template = Path(__file__).with_name('page_export.qs.in').read_text(encoding='utf-8')
    script = template.replace('__FUNCTION__', function).replace('__JOB_PATH__', json.dumps(job_path.as_posix(), ensure_ascii=True))
    (output / (function + '.qs')).write_text(script, encoding='utf-8')
    manifest = {'schema_version': 'nmr-export-job.v1', 'job_id': job_id,
                'source': str(source), 'source_sha256': before, 'working_copy': str(work),
                'function': function, 'job': job, 'native_execution': 'NOT_RUN',
                'software': str(software.resolve()) if software else None,
                'software_license_and_api': 'UNVERIFIED'}
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--software', type=Path)
    args = parser.parse_args()
    prepare(args.input, args.output, args.software)
    print('PREPARED: native execution and visual review have not run.')
