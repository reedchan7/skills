import copy
import unittest
import app


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
