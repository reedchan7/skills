"""Exercise baseline behavior, seeded faults, and held-out acceptance sanity.

Input cases are read-only. Every test and mutation runs in a fresh output copy.
This sanity check is for generated original fixtures, not grading refactor arms.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CASE_IDS = ['ledger', 'dispatch', 'credentials', 'legacy_report', 'labels', 'credits']
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cases', type=Path, help='Existing generated original case root; read-only.')
parser.add_argument('--output', type=Path, help='Fresh directory for disposable copies, logs and summary.')
args = parser.parse_args()
if args.output:
    output = args.output.resolve()
    if output.exists():
        parser.error('Output already exists; choose a fresh path: ' + str(output))
    output.mkdir(parents=True)
else:
    output = Path(tempfile.mkdtemp(prefix='refactor-self-check-'))

def run(command, cwd, log):
    result = subprocess.run(command, cwd=cwd, env=ENV, text=True,
                            capture_output=True, timeout=90)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text('$ ' + ' '.join(str(x) for x in command) + '\n'
                   + result.stdout + result.stderr)
    return result

def probe(case, repo, log, followup=False):
    command = [sys.executable, str(HERE / 'probe.py'), case, str(repo)]
    if followup:
        command.append('--followup')
    return run(command, repo, log)

def copy_repo(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=True)

if args.cases:
    cases = args.cases.resolve()
else:
    cases = output / 'cases'
    built = run([sys.executable, str(HERE / 'build_cases.py'), '--output', str(cases)],
                output, output / 'logs' / 'build.log')
    if built.returncode:
        raise SystemExit('Fixture build failed; inspect ' + str(output / 'logs' / 'build.log'))

expected_hashes = json.loads((HERE / 'fixture-input-hashes.json').read_text())
for rel, expected in expected_hashes.items():
    path = cases / rel
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit('Not an unchanged generated original fixture: ' + str(path))

results = []
for ident in CASE_IDS:
    repo = output / 'work' / 'baseline' / ident
    copy_repo(cases / ident / 'repo', repo)
    public = run([sys.executable, '-m', 'unittest', '-v'], repo,
                 output / 'logs' / ident / 'baseline-public.log')
    private = probe(ident, repo, output / 'logs' / ident / 'baseline-private.log')
    mutant = output / 'work' / 'mutant' / ident
    copy_repo(repo, mutant)
    mutation = json.loads((HERE / ident / 'mutant.json').read_text())
    app = mutant / 'app.py'
    source = app.read_text()
    if mutation['old'] not in source:
        raise SystemExit('Seed mutation anchor missing: ' + ident)
    app.write_text(source.replace(mutation['old'], mutation['new']))
    detected = probe(ident, mutant, output / 'logs' / ident / 'mutant.log')
    item = {'id': ident, 'public_baseline_pass': public.returncode == 0,
            'private_baseline_pass': private.returncode == 0,
            'mutant_detected': detected.returncode != 0}
    if ident in ['ledger', 'dispatch']:
        missing = probe(ident, repo, output / 'logs' / ident / 'followup-missing.log', True)
        item['heldout_missing_feature_detected'] = (
            missing.returncode != 0 and 'FAIL:' in missing.stderr
            and 'SyntaxError' not in missing.stderr and 'ERROR:' not in missing.stderr)
        positive = output / 'work' / 'followup-positive' / ident
        copy_repo(repo, positive)
        app = positive / 'app.py'
        source = app.read_text()
        if ident == 'ledger':
            old = "else:\n            amount = quantity * price"
            new = ("elif line.get('tier') == 'wholesale' and quantity >= 10:\n"
                   "            amount = quantity * price * Decimal('0.80')\n"
                   "        else:\n            amount = quantity * price")
        else:
            old = "if not hazardous:\n                                    if order['country'] == 'US':"
            new = ("if not hazardous:\n"
                   "                                    if order['weight_grams'] > 10000 and any(item.get('fragile', False) for item in order.get('items', [])):\n"
                   "                                        return {'eligible': False, 'cents': None, 'reason': 'express_fragile_weight', 'days': None}\n"
                   "                                    if order['country'] == 'US':")
        if old not in source:
            raise SystemExit('Positive control anchor missing: ' + ident)
        app.write_text(source.replace(old, new))
        accepted = probe(ident, positive, output / 'logs' / ident / 'followup-positive.log', True)
        item['heldout_positive_control_pass'] = accepted.returncode == 0
    results.append(item)

refused = run([sys.executable, str(HERE / 'build_cases.py'), '--output', str(cases)],
              output, output / 'logs' / 'overwrite-refused.log')
preserved = all(hashlib.sha256((cases / rel).read_bytes()).hexdigest() == expected
                for rel, expected in expected_hashes.items())
summary = {'cases': str(cases), 'output': str(output), 'results': results,
           'existing_output_overwrite_refused': refused.returncode != 0,
           'original_inputs_unchanged': preserved}
(output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
ok = all(all(value for key, value in item.items() if key != 'id') for item in results)
raise SystemExit(0 if ok and refused.returncode != 0 and preserved else 1)
