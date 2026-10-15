import sys,tempfile,unittest,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from source_copies import run

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.source=self.root/'来源.ai';self.source.write_bytes(b'SYNTHETIC NOT A VALID AI')
    def test_real_copy_and_hash(self):
        r=run([self.source],self.root/'other output');copy=Path(r['source_records'][0]['copy'])
        self.assertFalse(os.path.samefile(copy,self.source));self.assertEqual(copy.read_bytes(),self.source.read_bytes());copy.write_bytes(b'changed')
        self.assertEqual(self.source.read_bytes(),b'SYNTHETIC NOT A VALID AI')
    def test_no_output_inventory_and_no_native_claim(self):
        before=list(self.root.iterdir());r=run([self.source]);self.assertEqual(list(self.root.iterdir()),before);self.assertEqual(r['native_validation'],'NOT_PERFORMED')
    def test_same_basename_distinct_copies(self):
        folder=self.root/'second';folder.mkdir();second=folder/self.source.name;second.write_bytes(b'OTHER')
        r=run([self.source,second],self.root/'output')['source_records'];self.assertNotEqual(r[0]['copy'],r[1]['copy'])
    def test_existing_or_missing_paths_rejected(self):
        with self.assertRaises(ValueError):run([self.source],self.root)
        with self.assertRaises(ValueError):run([self.root/'missing.ai'],self.root/'out')

if __name__=='__main__':unittest.main()
