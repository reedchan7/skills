import argparse, pathlib, subprocess, sys, os
p=argparse.ArgumentParser()
p.add_argument('case')
p.add_argument('repo')
p.add_argument('--followup',action='store_true')
a=p.parse_args()
here=pathlib.Path(__file__).resolve().parent
repo=pathlib.Path(a.repo).resolve()
checks=[here/a.case/'probes.py']
if a.followup: checks.append(here/a.case/'followup_checks.py')
env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
failed=False
for path in checks:
    code="import sys,runpy,unittest; sys.path.insert(0,sys.argv[1]); d=runpy.run_path(sys.argv[2]); s=unittest.TestSuite(); [s.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(v)) for v in d.values() if isinstance(v,type) and issubclass(v,unittest.TestCase)]; r=unittest.TextTestRunner(verbosity=2).run(s); sys.exit(not r.wasSuccessful())"
    run=subprocess.run([sys.executable,'-c',code,str(repo),str(path)],cwd=repo,env=env)
    failed=failed or run.returncode != 0
sys.exit(failed)
