import copy
import unittest
import app


class OneShot:
    def __init__(self,values): self.values=values; self.used=False
    def __iter__(self):
        if self.used: raise AssertionError('iterated twice')
        self.used=True
        yield from self.values
class Probes(unittest.TestCase):
    def test_normalization_semantics(self):
        values=[' Straße ','STRASSE','a  b','a b','!A',None,'\t','İ','İ',' Z ']
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
