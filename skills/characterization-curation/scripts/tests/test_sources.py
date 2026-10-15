import sys,tempfile,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_sources import check

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'假资料.txt').write_bytes(b'SYNTHETIC SOURCE')
        self.row=dict(entry_id='e1',sample_id='A',batch_id='b1',modality='HRMS',selection='selected',status='candidate',reason='fixture',source='假资料.txt',sha256=hashlib.sha256(b'SYNTHETIC SOURCE').hexdigest(),locator='line 1')
    def test_source_hash_and_no_scientific_promotion(self):
        r=check({'entries':[self.row]},self.root);self.assertEqual(r['technical_status'],'PASS');self.assertEqual(r['scientific_review'],'NOT_PERFORMED')
        self.assertEqual((self.root/'假资料.txt').read_bytes(),b'SYNTHETIC SOURCE')
    def test_bad_hash_and_missing_source(self):
        for change in ({'sha256':'0'*64},{'source':'missing.txt'}):
            self.assertEqual(check({'entries':[{**self.row,**change}]},self.root)['technical_status'],'FAIL')
    def test_two_selected_sources_need_group(self):
        r2={**self.row,'entry_id':'e2'}
        self.assertEqual(check({'entries':[self.row,r2]},self.root)['technical_status'],'FAIL')
        rows=[{**r,'selection_group':'complementary'} for r in [self.row,r2]]
        r=check({'entries':rows},self.root);self.assertEqual(r['technical_status'],'PASS');self.assertEqual(len(r['shared_file_candidates']),1)
    def test_missing_distinct_from_unusable(self):
        r={**self.row,'selection':'candidate','status':'missing'}
        for key in ('source','sha256','locator'):del r[key]
        self.assertEqual(check({'entries':[r]},self.root)['entries'][0]['file_integrity'],'NOT_CHECKED')
        with self.assertRaises(ValueError):check({'entries':[{**r,'selection':'selected'}]},self.root)
    def test_duplicate_entry_rejected(self):
        with self.assertRaises(ValueError):check({'entries':[self.row,self.row]},self.root)

if __name__=='__main__':unittest.main()
