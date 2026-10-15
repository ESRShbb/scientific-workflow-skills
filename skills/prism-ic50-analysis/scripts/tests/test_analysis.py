"""Synthetic PZFX tables and fit rows; no native Prism or biological validation."""
import sys, tempfile, unittest, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pzfx_inventory import inventory
from summarize_fits import summarize
from read_result_labels import read
from prepare_native_export import prepare

class Tests(unittest.TestCase):
    def pzfx(self, ys, x='<Subcolumn><d>0</d><d>1</d></Subcolumn>'):
        t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup)
        p=Path(t.name)/'中文 sample.pzfx'
        p.write_text('<GraphPadPrismFile xmlns="urn:synthetic"><Table ID="T1"><Title>RT arbitrary</Title><XColumn>'+x+'</XColumn>'+ys+'</Table></GraphPadPrismFile>',encoding='utf-8')
        return p
    def test_preserves_all_five_subcolumns_and_blanks(self):
        p=self.pzfx('<YColumn><Title>sample-A</Title>'+ '<Subcolumn><d>1</d><d/></Subcolumn>'*5+'</YColumn>')
        before=p.read_bytes();r=inventory(p)['records'][0]
        self.assertEqual(len(r['y']),5); self.assertIsNone(r['y'][0][1]['value']);self.assertEqual(p.read_bytes(),before)
        self.assertEqual(r['table_title'],'RT arbitrary')
    def test_duplicates_are_retained_and_flagged(self):
        col='<YColumn><Title>A</Title><Subcolumn><d>1</d><d>2</d></Subcolumn></YColumn>'
        r=inventory(self.pzfx(col*2))['records'];self.assertEqual(len(r),2);self.assertEqual(r[1]['duplicate_of'],r[0]['record_id'])
    def test_unsupported_and_excluded_cells_not_coerced(self):
        r=inventory(self.pzfx('<YColumn><Subcolumn><d Excluded="1">bad</d></Subcolumn></YColumn>'))['records'][0]
        self.assertEqual(r['y'][0][0]['attributes']['Excluded'],'1');self.assertIsNone(r['y'][0][0]['value']);self.assertEqual(len(r['issues']),3)
    def rows(self):
        return [dict(sample_id='A',experiment_id=str(i),unit='nM',ic50=str(v),decision='include',reason='reviewed') for i,v in enumerate([10,100,1000])]
    def test_arithmetic_and_log_summaries(self):
        a=summarize(self.rows(),'arithmetic',3)['samples']['A'];g=summarize(self.rows(),'log',3)['samples']['A']
        self.assertEqual(a['summary']['arithmetic_mean'],370);self.assertAlmostEqual(g['summary']['geometric_mean'],100);self.assertEqual(g['summary']['sd_log10'],1)
    def test_exclusion_and_minimum_n(self):
        rows=self.rows();rows[0].update(decision='exclude',ic50='>10000',reason='censored')
        r=summarize(rows,'arithmetic',3)['samples']['A'];self.assertEqual(r['n'],2);self.assertIsNone(r['summary']);self.assertEqual(len(r['excluded']),1)
    def test_bad_units_duplicate_and_nonfinite_fail(self):
        rows=self.rows()
        for changed in ([*rows,rows[0]], [rows[0],{**rows[1],'unit':'uM'}], [{**rows[0],'ic50':'nan'}], [{**rows[0],'ic50':'>10'}]):
            with self.assertRaises(ValueError): summarize(changed,'arithmetic',1)
    def test_n_one_has_no_sd(self):
        r=summarize(self.rows()[:1],'arithmetic',1)['samples']['A']['summary'];self.assertIsNone(r['sample_sd'])
    def test_counts_distinguish_cells_from_independence(self):
        r=inventory(self.pzfx('<YColumn><Title>A</Title><Subcolumn><d>1</d><d/></Subcolumn><Subcolumn><d>2</d><d>3</d></Subcolumn></YColumn>'))
        self.assertEqual(r['counts']['y_data_cells'],4)
        self.assertEqual(r['counts']['finite_y_cells'],3);self.assertEqual(r['counts']['blank_y_cells'],1)
    def test_labeled_exports_preserve_repeated_labels_reject_numeric_only(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);p=Path(t.name)/'export.txt'
        p.write_text('Fit of Transform\nIC50\t12\t34\nIC50\t10 to 14\t30 to 38\n',encoding='utf-8')
        r=read(p,'utf-8','Fit of Transform');self.assertEqual(len(r['rows']),2)
        self.assertEqual(r['analysis_input'],'NOT_VERIFIED')
        with self.assertRaises(ValueError):read(p,'utf-8','Fit of Normalize')
        p.write_text('Fit of Transform\n12\t34\n',encoding='utf-8')
        with self.assertRaises(ValueError):read(p,'utf-8','Fit of Transform')
    def test_unverified_native_coordinates_rejected_before_copy(self):
        import json
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);root=Path(t.name)
        source=self.pzfx('<YColumn><Title>A</Title><Subcolumn><d>1</d><d>2</d></Subcolumn></YColumn>')
        spec=root/'sheets.json';spec.write_text(json.dumps({'sheets':[dict(number=1,verified=True,expected_title='Synthetic',evidence='synthetic fixture',columns=[1],parameters=[dict(row=5,label='TEST',verified=False,evidence='not checked')])]}),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'verified'):prepare(source,spec,root/'job')
        self.assertFalse((root/'job').exists())

if __name__=='__main__':unittest.main()
