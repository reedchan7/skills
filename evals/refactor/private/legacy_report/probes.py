import copy
import unittest
import app


import ast, contextlib, io, json, pathlib, subprocess, sys, tempfile
class Probes(unittest.TestCase):
    def test_boundaries_order_negative_and_zero(self):
        events=[dict(date=d,account=a,cents=c,status=s) for d,a,c,s in [
            ('2026-01-01','Z',9,'posted'),('2025-12-31','X',20,'posted'),
            ('2026-01-31','A',-4,'posted'),('2026-02-01','Y',60,'posted'),
            ('2026-01-08','Z',-9,'posted'),('2026-01-09','B',4,'void')]]
        before=copy.deepcopy(events)
        out=app.totals(events,'2026-01-01','2026-02-01')
        self.assertEqual(list(out.items()),[('Z',0),('A',-4)])
        self.assertEqual(app.render_report(events,'2026-01-01','2026-02-01'),'Z: 0\nA: -4\nTOTAL: -4\n')
        self.assertEqual(events,before)
        self.assertEqual(app.totals(events,'2026-03-01','2026-01-01'),{})
    def test_cli_and_import(self):
        root=pathlib.Path(app.__file__).parent
        with tempfile.TemporaryDirectory() as temp:
            p=pathlib.Path(temp)/'data.json'; p.write_text('[]')
            run=subprocess.run([sys.executable,str(root/'app.py'),'2026-01-01','2026-02-01',str(p)],capture_output=True,text=True)
            self.assertEqual((run.returncode,run.stdout,run.stderr),(0,'TOTAL: 0\n',''))
        run=subprocess.run([sys.executable,str(root/'app.py')],capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stdout,run.stderr),(2,'','usage: app.py START END INPUT.json\n'))
        code="import builtins; builtins.open=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('unexpected I/O')); import app"
        run=subprocess.run([sys.executable,'-c',code],cwd=root,capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stdout,run.stderr),(0,'',''))
    def test_parse_with_legacy_grammar(self):
        for p in pathlib.Path(app.__file__).parent.glob('*.py'):
            if not p.name.startswith('test'): ast.parse(p.read_text(),feature_version=(3,8))
