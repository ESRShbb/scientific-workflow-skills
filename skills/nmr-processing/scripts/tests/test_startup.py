import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inspect_script_startup import inspect_text

class StartupTests(unittest.TestCase):
    def test_definition_alone_is_not_execution(self):
        self.assertEqual(inspect_text('function f(){ serialization.open("x"); Application.quit(); }'),[])
    def test_try_caller_detected(self):
        r=inspect_text('function f(){ serialization.save("x"); }\ntry { f(); } catch(e){}')
        self.assertEqual(r[0]['line'],2)
        self.assertEqual(r[0]['operation'],'f()')
    def test_comments_and_strings(self):
        self.assertEqual(inspect_text('// Application.quit();\nvar text="serialization.save(x)";'),[])
    def test_transitive_call(self):
        self.assertTrue(inspect_text('function a(){ b(); } function b(){ serialization.open("x"); } a();'))

if __name__=='__main__':unittest.main()
