"""Job-preparation integrity, not native Illustrator acceptance."""
from pathlib import Path
import sys,tempfile,unittest,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_roundtrip import prepare

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.source=self.root/'合成 input.ai';self.source.write_bytes(b'SYNTHETIC NOT VALID AI')
    def test_verified_assets_copied_and_source_unchanged(self):
        image=self.root/'image.png';image.write_bytes(b'SYNTHETIC NOT PNG')
        spec=self.root/'assets.json';spec.write_text(json.dumps({'assets':[{'placed_index':0,'source':'image.png',
            'sha256':hashlib.sha256(image.read_bytes()).hexdigest()}]}),encoding='utf-8')
        before=self.source.read_bytes();r=prepare(self.source,self.root/'new job','embed',spec)
        self.assertEqual(Path(r['assets'][0]['copied']).read_bytes(),image.read_bytes())
        self.assertEqual(r['migration'],'NOT_VERIFIED');self.assertEqual(self.source.read_bytes(),before)
        with self.assertRaises(ValueError):prepare(self.source,self.root/'new job','embed',spec)
    def test_bad_hash_rejected_before_output_creation(self):
        spec=self.root/'assets.json';spec.write_text(json.dumps({'assets':[{'placed_index':0,'source':self.source.name,
            'sha256':'0'*64}]}),encoding='utf-8')
        with self.assertRaises(ValueError):prepare(self.source,self.root/'bad job','package',spec)
        self.assertFalse((self.root/'bad job').exists())

if __name__=='__main__':unittest.main()
