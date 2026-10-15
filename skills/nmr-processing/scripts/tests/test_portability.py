"""Synthetic fixtures: never valid scientific acquisitions/native application evidence."""
from pathlib import Path
import copy
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import raw_source_adapter as a
from prepare_export import prepare
from verify_export import verify, png_dimensions
from test_raw_source_adapter import _make_folder, _make_zip


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nmr synthetic ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def request(self):
        source = _make_zip(_make_folder(self.root), self.root / '原始 input.zip')
        base = {'path': str(source), 'sha256': a.sha256_file(source),
                'source_kind': 'bruker_zip', 'processing_profile': 'process_from_raw'}
        return {'spectrum_sources': {'1H': {**base, 'nucleus': '1H', 'experiment_id': '10'},
                                     '13C': {**base, 'nucleus': '13C', 'experiment_id': '11'}}}

    def test_shared_package_second_hash_does_not_bypass_check(self):
        req = self.request()
        req['spectrum_sources']['13C']['sha256'] = '0' * 64
        with self.assertRaises(a.RawSourceError):
            a.inventory_request(req, self.root / 'work')
        self.assertFalse((self.root / 'work').exists())

    def test_shared_package_second_profile_and_nucleus_checked(self):
        req = self.request()
        for field, value in [('processing_profile', 'curate_existing'), ('nucleus', '1H')]:
            changed = copy.deepcopy(req)
            changed['spectrum_sources']['13C'][field] = value
            with self.assertRaises(a.RawSourceError):
                a.inventory_request(changed, self.root / 'work')
        self.assertFalse((self.root / 'work').exists())

    def test_output_inside_source_rejected_without_writing(self):
        folder = _make_folder(self.root)
        source = {'path': str(folder), 'sha256': a.directory_manifest(folder)['tree_sha256'],
                  'source_kind': 'bruker_folder', 'nucleus': '1H', 'experiment_id': '10'}
        with self.assertRaises(a.RawSourceError):
            a.inventory_request({'spectrum_sources': {'1H': source}}, folder / 'work')
        self.assertFalse((folder / 'work').exists())

    def test_folder_requires_hash(self):
        folder = _make_folder(self.root)
        with self.assertRaises(a.RawSourceError):
            a.inspect_spectrum_source({'path': str(folder), 'source_kind': 'bruker_folder', 'experiment_id': '10'}, '1H')

    def test_windows_unsafe_zip_names(self):
        for name in ('a/../b', 'a//b', 'C:/a', 'a/x:y', 'a/NUL.txt', 'a/x.', 'a/./b'):
            with self.subTest(name=name):
                with self.assertRaises(a.RawSourceError):
                    a._safe_member_name(name)

    def test_zip_symlink_rejected(self):
        path = self.root / 'link.zip'
        item = zipfile.ZipInfo('link')
        item.create_system = 3
        item.external_attr = 0o120777 << 16
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr(item, '../outside')
        with self.assertRaises(a.RawSourceError):
            a.zip_manifest(path)

    def test_inventory_cli_relative_paths_and_no_overwrite(self):
        req = self.request()
        original = Path(req['spectrum_sources']['1H']['path'])
        before = a.sha256_file(original)
        for source in req['spectrum_sources'].values():
            source['path'] = original.name
        request_path = self.root / 'request.json'
        request_path.write_text(json.dumps(req), encoding='utf-8')
        output = self.root / 'report.json'
        cmd = [sys.executable, '-B', str(Path(a.__file__)), str(request_path), '--output', str(output),
               '--materialize-root', str(self.root / '复制 work')]
        result = subprocess.run(cmd, cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report_before = output.read_bytes()
        result = subprocess.run(cmd, cwd=self.root.parent, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), report_before)
        self.assertEqual(a.sha256_file(original), before)

    def test_export_preparation_unicode_paths_no_install(self):
        source = self.root / '已处理 sample.mnova'
        source.write_bytes(b'SYNTHETIC NOT A VALID MNOVA')
        before = a.sha256_file(source)
        out = self.root / 'other project 导图'
        manifest = prepare(source, out)
        self.assertEqual(manifest['native_execution'], 'NOT_RUN')
        self.assertEqual(a.sha256_file(Path(manifest['working_copy'])), before)
        script = (out / (manifest['function'] + '.qs')).read_text(encoding='utf-8')
        self.assertNotIn('__JOB_PATH__', script)
        self.assertIn('function ' + manifest['function'] + '()', script)
        self.assertEqual(a.sha256_file(source), before)
        with self.assertRaises(a.RawSourceError):
            prepare(source, out)

    def test_missing_software_and_missing_source(self):
        source = self.root / 'sample.mnova'
        source.write_bytes(b'SYNTHETIC')
        with self.assertRaisesRegex(ValueError, 'software'):
            prepare(source, self.root / 'output', self.root / 'missing.exe')
        with self.assertRaises(ValueError):
            prepare(self.root / 'missing.mnova', self.root / 'output')
        self.assertFalse((self.root / 'output').exists())

    def test_negative_boolean_and_missing_page_rejected(self):
        source = self.root / 'sample.mnova'
        source.write_bytes(b'SYNTHETIC')
        for page in (-1, True, None):
            with self.assertRaises(a.RawSourceError):
                a.inspect_spectrum_source({'path': str(source), 'source_kind': 'mnova_container',
                                           'sha256': a.sha256_file(source), 'page_index': page}, '1H')

    def test_marker_alone_is_not_native_success(self):
        source = self.root / 'sample.mnova'
        source.write_bytes(b'SYNTHETIC')
        out = self.root / 'out'
        prepare(source, out)
        (out / 'success.txt').write_text('SUCCESS')
        with self.assertRaises(FileNotFoundError):
            verify(out)

    def test_synthetic_report_validation_stays_visual_pending(self):
        source = self.root / 'sample.mnova'
        source.write_bytes(b'SYNTHETIC')
        out = self.root / 'out'
        m = prepare(source, out)
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
        png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\x00\xff\xff\xff')) + chunk(b'IEND', b'')
        (out / 'page_p1.png').write_bytes(png)
        report = {'job_id': m['job_id'], 'source': m['working_copy'], 'source_sha256': m['source_sha256'],
                  'saved_mnova': False, 'page_count': 1, 'pages': [{'page_number': 1,
                  'png': str(out / 'page_p1.png'), 'export_method': 'Page.toPixmap(300)'}]}
        (out / 'native_report.json').write_text(json.dumps(report), encoding='utf-8')
        (out / 'success.txt').write_text('SUCCESS')
        (out / 'native.log').write_text('SUCCESS 1 pages')
        self.assertEqual(verify(out)['overall'], 'NEEDS_VISUAL_REVIEW')
        self.assertEqual(verify(out)['process_exit'], 'UNVERIFIED')
        (out / 'attempt.json').write_text(json.dumps({'job_id':m['job_id'],'state':'TIMEOUT',
            'process_exited':False,'exit_code':None}),encoding='utf-8')
        self.assertEqual(verify(out)['technical_evidence'],'PASS')
        self.assertEqual(verify(out)['process_exit'],'CLEANUP_PENDING')
        self.assertEqual(verify(out)['overall'],'EXPORT_VERIFIED_EXECUTION_INCOMPLETE')
        (out / 'attempt.json').write_text(json.dumps({'job_id':m['job_id'],'state':'EXITED_UNVERIFIED',
            'process_exited':True,'exit_code':0}),encoding='utf-8')
        self.assertEqual(verify(out)['process_exit'],'PASS')
        report['job_id'] = 'stale'
        (out / 'native_report.json').write_text(json.dumps(report), encoding='utf-8')
        with self.assertRaises(ValueError):
            verify(out)
        (out / 'page_p1.png').write_bytes(png[:-4])
        with self.assertRaises(ValueError):
            png_dimensions(out / 'page_p1.png')


if __name__ == '__main__':
    unittest.main()
