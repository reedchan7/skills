from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, textwrap

import argparse

parser = argparse.ArgumentParser(description='Create six frozen offline refactor fixture repositories.')
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'cases', help='New case root; an existing path is never overwritten.')
args = parser.parse_args()
BASE = args.output.resolve()
if BASE.exists():
    parser.error('Output already exists; choose a fresh output path or explicitly remove it yourself: ' + str(BASE))
PUBLIC = BASE
PUBLIC.mkdir(parents=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding='utf-8')

CASES = []
def case(identifier, title, prompt, contract, source, tests, probes, criteria, mutant, followup=None):
    repo = PUBLIC / identifier / 'repo'
    repo.mkdir(parents=True, exist_ok=True)
    write(repo / 'app.py', source)
    write(repo / 'test_app.py', tests)
    write(repo / 'README.md', '# ' + title + '\n\n' + contract + '\n\nRun: `python3 -m unittest -v`\n')
    write(PUBLIC / identifier / 'TASK.md', prompt)
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@local.invalid', 'commit', '-qm', 'fixture baseline'], check=True)
    CASES.append({'id': identifier, 'title': title, 'repo': str(repo), 'task': str(PUBLIC / identifier / 'TASK.md'), 'test_command': 'python3 -m unittest -v', 'has_followup': bool(followup)})
    return repo

COMMON = '''
import copy
import unittest
import app

'''

case('ledger', 'Invoice exports', '''
Refactor the invoice export implementation so changes to billing calculations do not
need to be repeated in both formats. Keep this a small library and preserve all
documented output behavior. Make the change in this repository, run the existing
tests, and briefly explain the useful structural improvement. Do not add features
or change the public function signatures.
''', '''
The only public APIs are `export_json(invoice)` and `export_csv(invoice)` in app.py.
An invoice has id, customer, currency (informational), and lines. Each line has
sku, quantity (nonnegative integer), unit_price (decimal text), and optional tier.
Standard tier uses full price; member tier is 90%; unknown tiers use full price.
Round each line after multiplying quantity and applying its tier, to two decimal
places using decimal ROUND_HALF_UP. Total is the sum of rounded lines. Never mutate
the invoice. JSON is compact UTF-8-capable text, keys and arrays stay in input order,
all monetary values are two-place strings. CSV has CRLF, uses the standard CSV
escaping rules, has the header `invoice,customer,currency,sku,quantity,amount`, and
ends with a TOTAL row even for an empty invoice. The JSON currency default is USD,
as is CSV. Quantity and price conversion failures propagate to the caller.
''', '''
import csv
import io
import json
from decimal import Decimal, ROUND_HALF_UP


def export_json(invoice):
    rows = []
    total = Decimal('0.00')
    for line in invoice['lines']:
        quantity = int(line['quantity'])
        price = Decimal(line['unit_price'])
        if quantity < 0:
            raise ValueError('negative quantity')
        if line.get('tier') == 'member':
            amount = quantity * price * Decimal('0.90')
        else:
            amount = quantity * price
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total += amount
        rows.append({
            'sku': line['sku'],
            'quantity': quantity,
            'amount': format(amount, '.2f'),
        })
    output = {
        'invoice': invoice['id'],
        'customer': invoice['customer'],
        'currency': invoice.get('currency', 'USD'),
        'lines': rows,
        'total': format(total, '.2f'),
    }
    return json.dumps(output, ensure_ascii=False, separators=(',', ':'))


def export_csv(invoice):
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['invoice', 'customer', 'currency', 'sku', 'quantity', 'amount'])
    total = Decimal('0.00')
    for line in invoice['lines']:
        quantity = int(line['quantity'])
        price = Decimal(line['unit_price'])
        if quantity < 0:
            raise ValueError('negative quantity')
        if line.get('tier') == 'member':
            amount = quantity * price * Decimal('0.90')
        else:
            amount = quantity * price
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total += amount
        writer.writerow([
            invoice['id'],
            invoice['customer'],
            invoice.get('currency', 'USD'),
            line['sku'],
            quantity,
            format(amount, '.2f'),
        ])
    writer.writerow([
        invoice['id'], invoice['customer'], invoice.get('currency', 'USD'),
        'TOTAL', '', format(total, '.2f'),
    ])
    return output.getvalue()
''', COMMON + '''
class Exports(unittest.TestCase):
    def setUp(self):
        self.invoice = {'id': 'i1', 'customer': 'Ana', 'lines': [
            {'sku': 'tea', 'quantity': 3, 'unit_price': '2.50', 'tier': 'member'},
            {'sku': 'cup', 'quantity': 1, 'unit_price': '4.00'}]}

    def test_json(self):
        self.assertEqual(app.export_json(self.invoice), '{"invoice":"i1","customer":"Ana","currency":"USD","lines":[{"sku":"tea","quantity":3,"amount":"6.75"},{"sku":"cup","quantity":1,"amount":"4.00"}],"total":"10.75"}')

    def test_csv(self):
        self.assertEqual(app.export_csv(self.invoice), 'invoice,customer,currency,sku,quantity,amount\\r\\ni1,Ana,USD,tea,3,6.75\\r\\ni1,Ana,USD,cup,1,4.00\\r\\ni1,Ana,USD,TOTAL,,10.75\\r\\n')

    def test_input_is_unchanged(self):
        before = copy.deepcopy(self.invoice)
        app.export_json(self.invoice)
        app.export_csv(self.invoice)
        self.assertEqual(self.invoice, before)
''', COMMON + '''
import csv, io, json
from decimal import Decimal, ROUND_HALF_UP

class Probes(unittest.TestCase):
    def test_rounding_order_precision_escaping_and_parity(self):
        inv = {'id': 'a,"b', 'customer': '李\\n四', 'currency': 'JPY', 'lines': [
            {'sku': 'a', 'quantity': 1, 'unit_price': '0.005'},
            {'sku': 'a', 'quantity': 1, 'unit_price': '0.005'},
            {'sku': 'x,"', 'quantity': 3, 'unit_price': '0.15', 'tier': 'member'},
            {'sku': 'z', 'quantity': 2, 'unit_price': '1000000000.105', 'tier': 'other'}]}
        before = copy.deepcopy(inv)
        raw = app.export_json(inv)
        parsed = json.loads(raw)
        self.assertIn('李', raw)
        self.assertEqual(list(parsed), ['invoice','customer','currency','lines','total'])
        self.assertEqual([x['amount'] for x in parsed['lines']], ['0.01','0.01','0.41','2000000000.21'])
        self.assertEqual(parsed['total'], '2000000000.64')
        output = app.export_csv(inv)
        self.assertTrue(output.endswith('\\r\\n'))
        rows = list(csv.reader(io.StringIO(output)))
        self.assertEqual([x[-1] for x in rows[1:]], ['0.01','0.01','0.41','2000000000.21','2000000000.64'])
        self.assertEqual(rows[1][:4], ['a,"b','李\\n四','JPY','a'])
        self.assertEqual(inv, before)

    def test_empty_and_rejected_quantity(self):
        inv = {'id':'e','customer':'n','lines':[]}
        self.assertEqual(json.loads(app.export_json(inv))['total'], '0.00')
        self.assertEqual(len(list(csv.reader(io.StringIO(app.export_csv(inv))))), 2)
        inv['lines'] = [{'sku':'x','quantity':-1,'unit_price':'2'}]
        for export in [app.export_json, app.export_csv]:
            with self.assertRaises(ValueError): export(inv)

    def test_many_prices(self):
        for i in range(1, 90):
            price = Decimal(i) / 1000
            inv = {'id':'x','customer':'y','lines':[{'sku':'s','quantity':3,'unit_price':str(price),'tier':'member'}]}
            expected = format((3*price*Decimal('0.9')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), '.2f')
            self.assertEqual(json.loads(app.export_json(inv))['total'], expected)
            self.assertEqual(list(csv.reader(io.StringIO(app.export_csv(inv))))[-1][-1], expected)
''', {
    'useful_opportunity': 'Consolidate line billing policy while retaining distinct presentation concerns.',
    'quality_evidence': ['A future line-price policy change has one authoritative arithmetic location.', 'Format-specific CSV escaping and JSON shape remain understandable and local.', 'Intermediate data and helper APIs have cohesive roles; avoid a framework or general exporter registry for two fixed functions.'],
    'no_op_policy': 'A justified no-op is incomplete because duplicated arithmetic is a concrete maintenance problem.',
    'major_harms': ['Money rounding or decimal precision changes', 'Changed serialization or public API', 'Input mutation', 'Suppressed invalid input errors'],
}, {'old': "rounding=ROUND_HALF_UP", 'new': "rounding='ROUND_DOWN'"}, followup=('''
Add the wholesale billing tier: lines tagged wholesale receive 20% off only when
that individual line has quantity at least 10; below 10 they use full price.
Preserve member and unknown-tier behavior, per-line rounding, both output formats,
and all existing contracts. Add focused tests and implement the change.
''', COMMON + '''
import csv, io, json
class Followup(unittest.TestCase):
    def test_wholesale_is_per_line_and_shared(self):
        lines = [{'sku':'w','quantity':q,'unit_price':'0.105','tier':tier} for q,tier in [(9,'wholesale'),(10,'wholesale'),(11,'wholesale'),(10,'member'),(10,'unknown')]]
        inv = {'id':'f','customer':'c','lines':lines}
        expected = ['0.95','0.84','0.92','0.95','1.05']
        parsed = json.loads(app.export_json(inv))
        self.assertEqual([x['amount'] for x in parsed['lines']], expected)
        self.assertEqual(parsed['total'], '4.71')
        self.assertEqual([r[-1] for r in list(csv.reader(io.StringIO(app.export_csv(inv))))[1:-1]], expected)
    def test_no_combining_quantities(self):
        inv = {'id':'f','customer':'c','lines':[{'sku':'same','quantity':5,'unit_price':'1','tier':'wholesale'}]*2}
        self.assertEqual(json.loads(app.export_json(inv))['total'], '10.00')
'''))

case('dispatch', 'Shipping decision policy', '''
Refactor quote_shipping to make its branching policy easier to read and safely
maintain. Preserve decision precedence, reason codes, prices, and the public API.
Implement the refactoring and run the tests. Keep the solution proportionate to
this small offline rules module; no new policy engine or external dependencies.
''', '''
`quote_shipping(order)` returns {eligible, cents, reason, days}. Rejections have
cents=None and days=None. Inputs: country, weight_grams, optional items (each may
contain hazmat), service default standard, member default False, subtotal_cents
default 0, address_kind default street. Rule priority: (1) country outside US/CA
=> unsupported_country; (2) weight <=0 => invalid_weight; (3) weight >30000 =>
too_heavy; (4) any hazmat to CA => hazmat_border; (5) service other than standard/
express => unsupported_service; (6) express PO box => express_po_box; (7) express
hazmat => express_hazmat. Successful standard: US base 500, CA base 900; add 200
if >5000g; waive base for member subtotal >=5000; days 5 US or 8 CA, reason
standard. Express: US base 1500, CA base 2400; add 500 if >5000g; members get 300
off; days 1 US or 3 CA, reason express. Inputs are not mutated. Orders have valid
types and required country/weight. No network, clock, or configuration is involved.
''', '''
def quote_shipping(order):
    if order['country'] in ('US', 'CA'):
        if order['weight_grams'] > 0:
            if order['weight_grams'] <= 30000:
                hazardous = False
                for item in order.get('items', []):
                    if item.get('hazmat', False):
                        hazardous = True
                if order['country'] != 'CA' or not hazardous:
                    if order.get('service', 'standard') in ('standard', 'express'):
                        if order.get('service', 'standard') == 'express':
                            if order.get('address_kind', 'street') != 'po_box':
                                if not hazardous:
                                    if order['country'] == 'US':
                                        cents = 1500
                                        days = 1
                                    else:
                                        cents = 2400
                                        days = 3
                                    if order['weight_grams'] > 5000:
                                        cents += 500
                                    if order.get('member', False):
                                        cents -= 300
                                    return {'eligible': True, 'cents': cents, 'reason': 'express', 'days': days}
                                else:
                                    return {'eligible': False, 'cents': None, 'reason': 'express_hazmat', 'days': None}
                            else:
                                return {'eligible': False, 'cents': None, 'reason': 'express_po_box', 'days': None}
                        else:
                            if order['country'] == 'US':
                                cents = 500
                                days = 5
                            else:
                                cents = 900
                                days = 8
                            if order.get('member', False) and order.get('subtotal_cents', 0) >= 5000:
                                cents = 0
                            if order['weight_grams'] > 5000:
                                cents += 200
                            return {'eligible': True, 'cents': cents, 'reason': 'standard', 'days': days}
                    else:
                        return {'eligible': False, 'cents': None, 'reason': 'unsupported_service', 'days': None}
                else:
                    return {'eligible': False, 'cents': None, 'reason': 'hazmat_border', 'days': None}
            else:
                return {'eligible': False, 'cents': None, 'reason': 'too_heavy', 'days': None}
        else:
            return {'eligible': False, 'cents': None, 'reason': 'invalid_weight', 'days': None}
    else:
        return {'eligible': False, 'cents': None, 'reason': 'unsupported_country', 'days': None}
''', COMMON + '''
class Quotes(unittest.TestCase):
    def test_standard(self):
        self.assertEqual(app.quote_shipping({'country':'US','weight_grams':4000}), {'eligible':True,'cents':500,'reason':'standard','days':5})
    def test_express(self):
        self.assertEqual(app.quote_shipping({'country':'CA','weight_grams':6000,'service':'express','member':True}), {'eligible':True,'cents':2600,'reason':'express','days':3})
    def test_border(self):
        self.assertEqual(app.quote_shipping({'country':'CA','weight_grams':10,'items':[{'hazmat':True}]})['reason'], 'hazmat_border')
    def test_member_only_waives_base(self):
        self.assertEqual(app.quote_shipping({'country':'US','weight_grams':6000,'member':True,'subtotal_cents':5000})['cents'], 200)
''', COMMON + '''
import itertools

def expected(o):
    c, w, s = o['country'], o['weight_grams'], o['service']
    bad = [
        (c not in ('US','CA'), 'unsupported_country'),
        (w <= 0, 'invalid_weight'), (w > 30000, 'too_heavy'),
        (c == 'CA' and o['haz'], 'hazmat_border'),
        (s not in ('standard','express'), 'unsupported_service'),
        (s == 'express' and o['address_kind'] == 'po_box', 'express_po_box'),
        (s == 'express' and o['haz'], 'express_hazmat')]
    for condition, reason in bad:
        if condition: return {'eligible':False,'cents':None,'reason':reason,'days':None}
    if s == 'express':
        cost = {'US':1500,'CA':2400}[c] + (500 if w > 5000 else 0) - (300 if o['member'] else 0)
        days = {'US':1,'CA':3}[c]
    else:
        cost = 0 if o['member'] and o['subtotal_cents'] >= 5000 else {'US':500,'CA':900}[c]
        cost += 200 if w > 5000 else 0
        days = {'US':5,'CA':8}[c]
    return {'eligible':True,'cents':cost,'reason':s,'days':days}

class Probes(unittest.TestCase):
    def test_policy_cross_product(self):
        for c,w,s,h,p,m,total in itertools.product(['US','CA','FR'], [0,1,5000,5001,30000,30001], ['standard','express','drone'], [False,True], ['street','po_box'], [False,True], [4999,5000]):
            o = dict(country=c,weight_grams=w,service=s,haz=h,address_kind=p,member=m,subtotal_cents=total,items=[{'hazmat':False},{'hazmat':h}])
            before = copy.deepcopy(o)
            self.assertEqual(app.quote_shipping(o), expected(o), o)
            self.assertEqual(o, before)
    def test_defaults_and_empty_items(self):
        self.assertEqual(app.quote_shipping({'country':'CA','weight_grams':1,'items':[]}), {'eligible':True,'cents':900,'reason':'standard','days':8})
''', {
    'useful_opportunity': 'Expose policy order and separate success pricing from rejection decisions without hiding the rules behind machinery.',
    'quality_evidence': ['Readers can locate and change a rejection rule without tracing nested success branches.', 'Precedence is explicit and base fees/surcharges remain understandable.', 'Helpers or tables, if used, carry actual policy concepts rather than one wrapper per statement.'],
    'no_op_policy': 'Unchanged branching or cosmetic reformatting alone is incomplete.',
    'major_harms': ['Wrong rejection priority', 'Changed fee threshold or member discount', 'Input mutation', 'API or reason-code change']
}, {'old': "order['weight_grams'] > 5000", 'new': "order['weight_grams'] >= 5000"}, followup=('''
Add a fragile-item restriction: express shipping is unavailable for any order
containing an item with fragile=True when total order weight exceeds 10000 grams.
Use reason express_fragile_weight and the usual rejection shape. This new rule
comes after all existing rejection rules. Standard shipping and express orders
of exactly 10000 grams stay unchanged. Add focused tests and implement it.
''', COMMON + '''
class Followup(unittest.TestCase):
    def test_fragile_rule_and_priority(self):
        for country in ['US','CA']:
            for weight in [10000,10001]:
                o = {'country':country,'weight_grams':weight,'service':'express','items':[{}, {'fragile':True}]}
                out = app.quote_shipping(o)
                if weight > 10000:
                    self.assertEqual(out, {'eligible':False,'cents':None,'reason':'express_fragile_weight','days':None})
                else: self.assertTrue(out['eligible'])
        o = {'country':'US','weight_grams':10001,'service':'express','items':[{'fragile':True,'hazmat':True}],'address_kind':'po_box'}
        self.assertEqual(app.quote_shipping(o)['reason'],'express_po_box')
        o['address_kind'] = 'street'
        self.assertEqual(app.quote_shipping(o)['reason'],'express_hazmat')
        o['items'][0]['hazmat'] = False
        o['service'] = 'standard'
        self.assertTrue(app.quote_shipping(o)['eligible'])
        o['service'] = 'express'
        o['weight_grams'] = 30001
        self.assertEqual(app.quote_shipping(o)['reason'],'too_heavy')
'''))

case('credentials', 'Credential rotation boundary', '''
Refactor rotate_token so its authorization, token preparation, and side-effect
sequence are easier to review. Preserve the existing API and failure behavior,
including call order. Implement the refactoring and test it. This module runs
offline against injected services; keep those boundaries and do not add I/O.
''', '''
Public API: rotate_token(actor, account_id, label, store, issuer, audit, clock).
actor has id and role. Only admins proceed; others get PermissionError('admin
required') before any injected service is called. Then store.get_account(id)
returns a dict or None; missing => LookupError('account not found'), inactive =>
ValueError('account inactive'), then a non-string/blank label => ValueError('label
required'). Label strips outer whitespace and truncates to 32 chars. Then call
clock(), issuer.issue(account_id), and SHA-256 the UTF-8 token. Call store.replace
with account id and {digest, label, created_at}. Then audit.record with event
token_rotated, actor_id, account_id, created_at. Return {account_id, token, label}.
The raw token is returned to the authorized caller only; it never enters store or
audit. No writes on validation failures. Issuer/clock/store/audit errors propagate;
audit is called only after a successful replace. An audit failure occurs after
the replacement and propagates (there is no transaction or compensation API).
Never mutate actor or an account object returned by store. Services are duck-typed;
no persistent global state, network, filesystem, time, or random operations.
''', '''
import hashlib


def rotate_token(actor, account_id, label, store, issuer, audit, clock):
    if actor.get('role') != 'admin':
        raise PermissionError('admin required')
    account = store.get_account(account_id)
    if account is None:
        raise LookupError('account not found')
    if not account['active']:
        raise ValueError('account inactive')
    if not isinstance(label, str) or not label.strip():
        raise ValueError('label required')
    label = label.strip()[:32]
    created_at = clock()
    token = issuer.issue(account_id)
    digest = hashlib.sha256(token.encode('utf-8')).hexdigest()
    store.replace(account_id, {
        'digest': digest,
        'label': label,
        'created_at': created_at,
    })
    audit.record({
        'event': 'token_rotated',
        'actor_id': actor['id'],
        'account_id': account_id,
        'created_at': created_at,
    })
    return {'account_id': account_id, 'token': token, 'label': label}
''', COMMON + '''
from unittest.mock import Mock
class Rotation(unittest.TestCase):
    def test_success(self):
        store = Mock()
        store.get_account.return_value = {'active': True}
        issuer = Mock()
        issuer.issue.return_value = 'new-token'
        audit = Mock()
        result = app.rotate_token({'id':'u','role':'admin'}, 'a', ' App ', store, issuer, audit, lambda: 10)
        self.assertEqual(result, {'account_id':'a','token':'new-token','label':'App'})
        self.assertNotIn('token', store.replace.call_args.args[1])
        audit.record.assert_called_once()
    def test_unauthorized(self):
        store = Mock()
        with self.assertRaises(PermissionError):
            app.rotate_token({'id':'u','role':'viewer'}, 'a', 'App', store, Mock(), Mock(), lambda:10)
        store.get_account.assert_not_called()
''', COMMON + '''
import hashlib
class Services:
    def __init__(self, fail=None, account=None):
        self.events=[]
        self.fail=fail
        self.account={'active':True} if account is None else account
        self.saved=None
    def call(self, name, *args):
        self.events.append((name, copy.deepcopy(args)))
        if name == self.fail: raise RuntimeError(name)
    def get_account(self, ident):
        self.call('get',ident)
        return None if self.account == 'missing' else self.account
    def clock(self): self.call('clock'); return 17
    def issue(self, ident): self.call('issue',ident); return 'sëcret\\n'
    def replace(self, ident, value): self.call('replace',ident,value); self.saved=value
    def record(self, value): self.call('audit',value)

def run(s, actor=None, label=' Key '):
    return app.rotate_token(actor or {'id':'u','role':'admin'}, 'acct', label, s,s,s,s.clock)

class Probes(unittest.TestCase):
    def test_order_and_data_boundaries(self):
        s=Services(); actor={'id':'u','role':'admin'}; before=copy.deepcopy(actor)
        result=run(s,actor,' '+ 'x'*40 +' ')
        self.assertEqual([e[0] for e in s.events],['get','clock','issue','replace','audit'])
        self.assertEqual(result,{'account_id':'acct','token':'sëcret\\n','label':'x'*32})
        self.assertEqual(s.saved, {'digest':hashlib.sha256('sëcret\\n'.encode()).hexdigest(),'label':'x'*32,'created_at':17})
        self.assertEqual(s.events[-1][1][0],{'event':'token_rotated','actor_id':'u','account_id':'acct','created_at':17})
        self.assertNotIn('sëcret', repr(s.events)); self.assertEqual(actor,before); self.assertEqual(s.account,{'active':True})
    def test_each_failure_stops_sequence(self):
        names=['get','clock','issue','replace','audit']
        for name in names:
            s=Services(fail=name)
            with self.assertRaisesRegex(RuntimeError,name): run(s)
            self.assertEqual([e[0] for e in s.events],names[:names.index(name)+1])
            self.assertEqual(s.saved is not None, name=='audit')
    def test_invalid_and_precedence(self):
        s=Services(fail='get')
        with self.assertRaisesRegex(PermissionError,'admin required'): run(s,{'id':'u','role':'viewer'},'')
        self.assertEqual(s.events,[])
        for account, error, message in [('missing',LookupError,'account not found'),({'active':False},ValueError,'account inactive'),({'active':True},ValueError,'label required')]:
            s=Services(account=account)
            with self.assertRaisesRegex(error,message): run(s,label=' ')
            self.assertEqual([e[0] for e in s.events],['get'])
        for value in [None, 1, []]:
            s=Services()
            with self.assertRaisesRegex(ValueError,'label required'): run(s,label=value)
            self.assertEqual([e[0] for e in s.events],['get'])
''', {
    'useful_opportunity': 'Improve reviewability of the authorization and data-preparation boundary without obscuring sequential effects.',
    'quality_evidence': ['Top-level sequencing makes authorization-before-read and replace-before-audit visible.', 'Any extracted pure preparation helper groups real transformations, with little parameter plumbing.', 'Security-relevant control flow remains locally inspectable; no generic callback pipeline or compensation invented.'],
    'no_op_policy': 'A concise, justified decision to retain the sequence can earn restraint credit, but requested implemented improvement still needs an observable reviewability benefit; cosmetic-only maximum usefulness 1.',
    'major_harms': ['Unauthorized reads or writes', 'Secret in stored or audit data', 'Swallowed errors or changed side-effect order', 'Invented rollback/double issuance', 'Mutation of service-owned objects']
}, {'old': "'digest': digest", 'new': "'digest': token"})

repo = case('legacy_report', 'Legacy report with existing edits', '''
Refactor the duplicated event selection logic in totals and render_report so it
is maintained consistently. Preserve the CLI and legacy formatting exactly. The
worktree already contains a colleague's incomplete local edits and a scratch file;
preserve them. Scope is app.py plus relevant tests only. Implement the refactoring,
run tests, and report what changed without committing or cleaning the worktree.
''', '''
Python stdlib only; this tool is also copied into legacy Python 3.8 installations,
so do not introduce syntax or APIs requiring later versions. Public APIs are
totals(events, start, end), render_report(events, start, end), and CLI
`python3 app.py START END INPUT.json`. Dates are ISO YYYY-MM-DD strings; range is
start inclusive/end exclusive. Events have date, account, cents, status; select
status=posted only. Preserve encounter order of accounts, including zero/negative
totals. totals returns a normal dict. render_report returns lines `account: cents`,
then `TOTAL: cents`, always ending with LF, even when empty. CLI emits the rendered
text exactly once; wrong arg count prints `usage: app.py START END INPUT.json` to
stderr with exit 2; JSON/file errors propagate. Importing app performs no I/O and
does not consume arguments. Inputs are not mutated. Existing tracked operations.md
and untracked operator-draft.txt are outside your editing scope.
''', '''
import json
import sys


def totals(events, start, end):
    output = {}
    for event in events:
        if event['status'] != 'posted':
            continue
        if event['date'] < start:
            continue
        if event['date'] >= end:
            continue
        account = event['account']
        if account not in output:
            output[account] = 0
        output[account] += event['cents']
    return output


def render_report(events, start, end):
    accounts = {}
    for event in events:
        if event['status'] != 'posted':
            continue
        if event['date'] < start:
            continue
        if event['date'] >= end:
            continue
        account = event['account']
        if account not in accounts:
            accounts[account] = 0
        accounts[account] += event['cents']
    lines = []
    grand_total = 0
    for account, cents in accounts.items():
        lines.append('{}: {}'.format(account, cents))
        grand_total += cents
    lines.append('TOTAL: {}'.format(grand_total))
    return '\\n'.join(lines) + '\\n'


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 3:
        print('usage: app.py START END INPUT.json', file=sys.stderr)
        return 2
    start, end, filename = argv
    with open(filename, encoding='utf-8') as handle:
        events = json.load(handle)
    sys.stdout.write(render_report(events, start, end))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
''', COMMON + '''
class Reports(unittest.TestCase):
    def test_selected_totals(self):
        events=[{'date':'2026-01-01','account':'B','cents':10,'status':'posted'}, {'date':'2026-01-02','account':'B','cents':40,'status':'pending'}]
        self.assertEqual(app.totals(events,'2026-01-01','2026-02-01'),{'B':10})
        self.assertEqual(app.render_report(events,'2026-01-01','2026-02-01'),'B: 10\\nTOTAL: 10\\n')
    def test_empty(self):
        self.assertEqual(app.render_report([],'2026-01-01','2026-02-01'),'TOTAL: 0\\n')
''', COMMON + '''
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
        self.assertEqual(app.render_report(events,'2026-01-01','2026-02-01'),'Z: 0\\nA: -4\\nTOTAL: -4\\n')
        self.assertEqual(events,before)
        self.assertEqual(app.totals(events,'2026-03-01','2026-01-01'),{})
    def test_cli_and_import(self):
        root=pathlib.Path(app.__file__).parent
        with tempfile.TemporaryDirectory() as temp:
            p=pathlib.Path(temp)/'data.json'; p.write_text('[]')
            run=subprocess.run([sys.executable,str(root/'app.py'),'2026-01-01','2026-02-01',str(p)],capture_output=True,text=True)
            self.assertEqual((run.returncode,run.stdout,run.stderr),(0,'TOTAL: 0\\n',''))
        run=subprocess.run([sys.executable,str(root/'app.py')],capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stdout,run.stderr),(2,'','usage: app.py START END INPUT.json\\n'))
        code="import builtins; builtins.open=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('unexpected I/O')); import app"
        run=subprocess.run([sys.executable,'-c',code],cwd=root,capture_output=True,text=True)
        self.assertEqual((run.returncode,run.stdout,run.stderr),(0,'',''))
    def test_parse_with_legacy_grammar(self):
        for p in pathlib.Path(app.__file__).parent.glob('*.py'):
            if not p.name.startswith('test'): ast.parse(p.read_text(),feature_version=(3,8))
''', {
    'useful_opportunity': 'Make event selection and accumulation consistent across direct and text APIs while respecting the mixed worktree.',
    'quality_evidence': ['One authoritative selection/accumulation policy avoids divergent fixes.', 'Rendering and CLI remain straightforward and output ownership remains clear.', 'Changes stay in the requested code/test scope and use Python 3.8-compatible APIs.'],
    'no_op_policy': 'Unchanged duplication is incomplete.',
    'major_harms': ['Loss or modification of pre-existing tracked/untracked edits', 'Changed CLI or report format/order', 'Range/status mistakes', 'New import side effects or legacy incompatibility']
}, {'old': "event['date'] >= end", 'new': "event['date'] > end"})
write(repo / 'operations.md', 'Legacy export notes\n\nPreserve account encounter order for downstream operator diffs.\n')
subprocess.run(['git','-C',str(repo),'add','operations.md'],check=True)
subprocess.run(['git','-C',str(repo),'-c','user.name=Fixture','-c','user.email=fixture@local.invalid','commit','-qm','document operations'],check=True)
write(repo / 'operations.md', 'Legacy export notes\n\nPreserve account encounter order for downstream operator diffs.\n\nDRAFT by operator: reconcile the January adjustments before running export.\n')
write(repo / 'operator-draft.txt', 'Unfinished colleague scratchpad; preserve exactly.\nJanuary offset = -17 cents, awaiting approval.\n')

case('labels', 'Small tag normalization cleanup', '''
Make a small refactor to remove the repeated tag normalization in tags_for_search
and tags_for_display. Preserve their different ordering rules and all public
behavior. This is a bounded cleanup: keep the module easy to read and avoid adding
configuration or dependencies. Implement the change and run the tests.
''', '''
Public APIs: tags_for_search(values), tags_for_display(values). values is an
iterable of strings/None; normalize each non-None string with strip().lower(),
discard empty strings, deduplicate normalized values. Search returns a sorted
tuple. Display returns a list in first-encounter order. Consume one-shot iterables
once; do not mutate input containers. This is Python lower(), not casefold(), and
only outer whitespace is stripped; internal whitespace/punctuation stay intact.
''', '''
def tags_for_search(values):
    result = set()
    for value in values:
        if value is None:
            continue
        normalized = value.strip().lower()
        if not normalized:
            continue
        result.add(normalized)
    return tuple(sorted(result))


def tags_for_display(values):
    result = []
    seen = set()
    for value in values:
        if value is None:
            continue
        normalized = value.strip().lower()
        if not normalized:
            continue
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result
''', COMMON + '''
class Tags(unittest.TestCase):
    def test_search(self):
        self.assertEqual(app.tags_for_search([' B ','a','b',None,' ']),('a','b'))
    def test_display(self):
        self.assertEqual(app.tags_for_display([' B ','a','b',None,' ']),['b','a'])
''', COMMON + '''
class OneShot:
    def __init__(self,values): self.values=values; self.used=False
    def __iter__(self):
        if self.used: raise AssertionError('iterated twice')
        self.used=True
        yield from self.values
class Probes(unittest.TestCase):
    def test_normalization_semantics(self):
        values=[' Straße ','STRASSE','a  b','a b','!A',None,'\\t','İ','İ',' Z ']
        before=list(values)
        display=['straße','strasse','a  b','a b','!a','i̇','z']
        self.assertEqual(app.tags_for_display(OneShot(values)),display)
        self.assertEqual(app.tags_for_search(OneShot(values)),tuple(sorted(display)))
        self.assertEqual(values,before)
    def test_empty_and_fresh_results(self):
        self.assertEqual(app.tags_for_search(iter(())),())
        self.assertEqual(app.tags_for_display(iter(())),[])
        old=app.tags_for_display(['a']); old.append('b')
        self.assertEqual(app.tags_for_display(['a']),['a'])
''', {
    'useful_opportunity': 'Share the actual normalization policy while keeping the two small ordering contracts obvious.',
    'quality_evidence': ['Normalization semantics have one maintained implementation.', 'Search sorting and display encounter order remain easily distinguishable.', 'No unnecessary class, strategy, configuration, or broad API change; overhead stays proportionate.'],
    'no_op_policy': 'No-op/cosmetic-only does not satisfy requested cleanup.',
    'major_harms': ['Changed Unicode or whitespace semantics', 'Changed ordering or return types', 'Double consumption of iterable', 'State leakage across calls']
}, {'old': '.lower()', 'new': '.casefold()'})

case('credits', 'Similar arithmetic, separate policies', '''
Review the repeated-looking arithmetic in earned_points and refund_points and
refactor only if there is a useful shared concept. Preserve existing policies and
keep future policy changes local. If combining them would make the code harder
to maintain, leave those functions separate and explain your judgment with a
concrete example from the current contracts. You may add a focused test if it
clarifies the boundary. Do not introduce a framework or change features.
''', '''
These are separate business policies exposed as app.earned_points(cents, member)
and app.refund_points(cents, original_multiplier). Both return int and clamp
negative cents to zero. earned_points awards floor(cents / 100) whole points and
then doubles the integer for members (bool). refund_points removes points from a
prior purchase using its recorded integer multiplier (1, 2, or 3), multiplying
cents first and then taking floor(... / 100). Multipliers are historically fixed
for refunds even when current earning policy changes. 150 cents for a member
earns 2 points; refunding 150 cents with original_multiplier=2 removes 3 points.
Inputs have documented types; no other validation is required. Two helpers,
summarize_earnings and summarize_refunds, aggregate per-entry decisions and must
preserve row-level rounding. They return {entries, points}; empty inputs produce
zero for both. Inputs and nested objects must remain unchanged. Pure offline code.
''', '''
def earned_points(cents, member):
    cents = max(0, cents)
    points = cents // 100
    if member:
        points = points * 2
    return points


def refund_points(cents, original_multiplier):
    cents = max(0, cents)
    points = cents * original_multiplier
    points = points // 100
    return points


def summarize_earnings(purchases):
    count = 0
    points = 0
    for purchase in purchases:
        count += 1
        points += earned_points(purchase['cents'], purchase['member'])
    return {'entries': count, 'points': points}


def summarize_refunds(refunds):
    count = 0
    points = 0
    for refund in refunds:
        count += 1
        points += refund_points(refund['cents'], refund['original_multiplier'])
    return {'entries': count, 'points': points}
''', COMMON + '''
class Points(unittest.TestCase):
    def test_two_policies(self):
        self.assertEqual(app.earned_points(150,True),2)
        self.assertEqual(app.refund_points(150,2),3)
    def test_summaries(self):
        self.assertEqual(app.summarize_earnings([{'cents':150,'member':True}]),{'entries':1,'points':2})
        self.assertEqual(app.summarize_refunds([]),{'entries':0,'points':0})
''', COMMON + '''
class Probes(unittest.TestCase):
    def test_policy_boundaries(self):
        for cents in [-200,-1,0,1,33,34,50,99,100,149,150,199,200,10001]:
            for member in [False,True]:
                self.assertEqual(app.earned_points(cents,member),(max(0,cents)//100)*(2 if member else 1))
            for multiplier in [1,2,3]:
                self.assertEqual(app.refund_points(cents,multiplier),(max(0,cents)*multiplier)//100)
    def test_row_rounding_and_no_mutation(self):
        purchases=[{'cents':50,'member':True},{'cents':50,'member':True}]
        refunds=[{'cents':34,'original_multiplier':3},{'cents':34,'original_multiplier':3}]
        before=copy.deepcopy((purchases,refunds))
        self.assertEqual(app.summarize_earnings(iter(purchases)),{'entries':2,'points':0})
        self.assertEqual(app.summarize_refunds(iter(refunds)),{'entries':2,'points':2})
        self.assertEqual((purchases,refunds),before)
''', {
    'useful_opportunity': 'Exercise judgment about accidental textual similarity versus independently evolving policies.',
    'quality_evidence': ['Earning and refund rounding differences remain explicit.', 'No shared rounding switch or flags create unnecessary coupling between historical and current policy.', 'A justified no-op cites a concrete contractual divergence; a small useful clarity/test improvement also counts if it preserves locality.'],
    'no_op_policy': 'A documented decision to retain separation with a correct concrete example is full completion. Silent no-op, generic refusal, or unexecuted plan is incomplete.',
    'major_harms': ['Reordered rounding changes points', 'Coupling current earning multiplier to historical refunds', 'Aggregation before row-level rounding', 'Input mutation']
}, {'old': 'points = cents * original_multiplier\n    points = points // 100', 'new': 'points = (cents // 100) * original_multiplier'})

write(PUBLIC / 'manifest.json', json.dumps({'schema':1,'cases':CASES,'instructions':'Give each arm only its TASK.md and a fresh copy of repo, including git metadata and dirty files. Do not expose private evaluation material or other outputs. Record final response alongside output tree. Public tests are runnable from each repo. No network or external writes are needed.'},indent=2))

print(json.dumps({'case_root': str(PUBLIC), 'case_ids': [item['id'] for item in CASES], 'manifest': str(PUBLIC / 'manifest.json')}, indent=2))
