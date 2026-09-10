import copy
import unittest
import app


import csv, io, json
from decimal import Decimal, ROUND_HALF_UP

class Probes(unittest.TestCase):
    def test_rounding_order_precision_escaping_and_parity(self):
        inv = {'id': 'a,"b', 'customer': '李\n四', 'currency': 'JPY', 'lines': [
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
        self.assertTrue(output.endswith('\r\n'))
        rows = list(csv.reader(io.StringIO(output)))
        self.assertEqual([x[-1] for x in rows[1:]], ['0.01','0.01','0.41','2000000000.21','2000000000.64'])
        self.assertEqual(rows[1][:4], ['a,"b','李\n四','JPY','a'])
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
