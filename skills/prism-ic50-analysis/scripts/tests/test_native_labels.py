import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prepare=module('prepare_native_export').prepare;read=module('read_result_labels').read
class NativeLabels(unittest.TestCase):
    def test_native_export_uses_verified_sheet_without_row_guess(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);src=p/'source.pzfx';src.write_text('<GraphPadPrismFile/>')
            mapping=p/'map.json';mapping.write_text(json.dumps({'sheets':[{'number':2,'expected_title':'fit','verified':True,'evidence':'native title'}]}))
            result=prepare(src,mapping,p/'job',label_mode='native')
            self.assertEqual(result['label_provenance'],'NATIVE_EXPORTTABLE')
            self.assertEqual((p/'job/working.pzfx').read_bytes(),src.read_bytes())
            self.assertIn('ExportTable ',(p/'job/export.pzc').read_text())
    def test_native_table_keeps_repeated_parameter_sections(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);title=p/'title.txt';title.write_text('fit\n');table=p/'table.txt'
            table.write_text('\tA\tB\nIC50\t2\t3\n95% CI\t\t\nIC50\t??? to 4\t1 to ???\n')
            r=read(table,'utf-8','fit',title)
            self.assertEqual([x['cells'] for x in r['rows'] if x['label']=='IC50'],[['2','3'],['??? to 4','1 to ???']])
            with self.assertRaises(ValueError):read(table,'utf-8','different fit',title)
