import copy
import unittest
import app


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
