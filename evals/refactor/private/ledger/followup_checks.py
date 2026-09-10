import copy
import unittest
import app


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
