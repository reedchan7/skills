import copy
import unittest
import app


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
    def issue(self, ident): self.call('issue',ident); return 'sëcret\n'
    def replace(self, ident, value): self.call('replace',ident,value); self.saved=value
    def record(self, value): self.call('audit',value)

def run(s, actor=None, label=' Key '):
    return app.rotate_token(actor or {'id':'u','role':'admin'}, 'acct', label, s,s,s,s.clock)

class Probes(unittest.TestCase):
    def test_order_and_data_boundaries(self):
        s=Services(); actor={'id':'u','role':'admin'}; before=copy.deepcopy(actor)
        result=run(s,actor,' '+ 'x'*40 +' ')
        self.assertEqual([e[0] for e in s.events],['get','clock','issue','replace','audit'])
        self.assertEqual(result,{'account_id':'acct','token':'sëcret\n','label':'x'*32})
        self.assertEqual(s.saved, {'digest':hashlib.sha256('sëcret\n'.encode()).hexdigest(),'label':'x'*32,'created_at':17})
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
