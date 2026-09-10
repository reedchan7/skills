import copy
import unittest
import app


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
