"""Synthetic XML and ZIP contracts; not native ChemDraw/Office validation."""
import sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inspect_cdxml import inspect as cdxml
from inspect_office_ole import inspect as office
from inspect_office_ole import compare

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.xml='<CDXML><page id="1"><fragment id="2"><n id="3" p="0 0"/><n id="4" Element="8" Isotope="18"/><b id="5" B="3" E="4" Order="2"/></fragment></page></CDXML>'
    def parse(self,text):
        p=self.root/'sample.cdxml';p.write_text(text,encoding='utf-8');return cdxml(p)
    def test_coordinates_do_not_change_snapshot(self):
        a=self.parse(self.xml);b=self.parse(self.xml.replace('p="0 0"','p="10 20"'))
        self.assertEqual(a['semantic_snapshot_sha256'],b['semantic_snapshot_sha256']);self.assertEqual(a['xml_integrity'],'PASS')
    def test_isotope_charge_bond_changes_are_detected(self):
        base=self.parse(self.xml)['semantic_snapshot_sha256']
        for edited in (self.xml.replace('18','16'),self.xml.replace('Element="8"','Element="8" Charge="1"'),self.xml.replace('Order="2"','Order="1"')):
            self.assertNotEqual(self.parse(edited)['semantic_snapshot_sha256'],base)
    def test_missing_endpoint_and_duplicate_id(self):
        self.assertEqual(self.parse(self.xml.replace('E="4"','E="99"'))['xml_integrity'],'FAIL')
        self.assertEqual(self.parse(self.xml.replace('id="4"','id="3"'))['xml_integrity'],'FAIL')
    def make_office(self,missing=False,external=False):
        path=self.root/'sample.docx'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('word/document.xml','<w:document xmlns:w="urn:w" xmlns:o="urn:o" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><o:OLEObject ProgID="ChemDraw.Document.6.0" r:id="r1"/></w:document>')
            z.writestr('word/_rels/document.xml.rels','<Relationships><Relationship Id="r1" Target="embeddings/custom-name.bin"'+(' TargetMode="External"' if external else '')+'/></Relationships>')
            if not missing:z.writestr('word/embeddings/custom-name.bin',b'SYNTHETIC VjCD0100 NOT VALID OLE')
        return path
    def test_custom_embedding_and_no_editability_claim(self):
        r=office(self.make_office());self.assertEqual(r['objects'][0]['status'],'EMBEDDING_PRESENT');self.assertEqual(r['native_editability'],'NOT_VERIFIED')
    def test_missing_payload_and_external_links(self):
        self.assertEqual(office(self.make_office(missing=True))['relationship_integrity'],'FAIL')
        self.assertEqual(office(self.make_office(external=True))['objects'][0]['status'],'EXTERNAL_LINK')
    def test_geometry_change_is_reported_even_when_payload_unchanged(self):
        import copy
        before=office(self.make_office());after=copy.deepcopy(before)
        before['objects'][0]['display_geometry']=[{'type':'shape','attributes':{'style':'width:155.35pt'}}]
        after['objects'][0]['display_geometry']=[{'type':'shape','attributes':{'style':'width:157.25pt'}}]
        r=compare(before,after)
        self.assertFalse(r['same_relationship_snapshot']);self.assertEqual(r['changes'][0]['changed_fields'],['display_geometry'])
        self.assertEqual(r['chemical_equivalence'],'NOT_PROVEN')
    def test_reused_relationship_id_does_not_bind_changed_payload(self):
        import copy
        before=office(self.make_office());after=copy.deepcopy(before)
        after['objects'][0]['sha256']='new-payload'
        r=compare(before,after)
        self.assertEqual(len(r['unmatched_before']),1);self.assertEqual(r['changes'],[])
        mapping={'objects':[{'before':['word/document.xml','r1'],'after':['word/document.xml','r1'],'evidence':'synthetic verified identity'}]}
        r=compare(before,after,mapping);self.assertEqual(r['changes'][0]['changed_fields'],['sha256'])

if __name__=='__main__':unittest.main()
