import unittest
import src.logical_statements as ls


class LogicalStatementsTest(unittest.TestCase):
    def test_value(self):
        v = ls.Value("a")
        self.assertTrue(v.finished())
        self.assertEqual(str(v), "a")

    def test_not_fin(self):
        n = ls.Not(ls.Value("a"))
        self.assertTrue(n.finished())
        self.assertEqual(str(n), "~a")

    def test_not_cont(self):
        n = ls.Not(ls.And(ls.Value("a"), ls.Value("b")))
        self.assertFalse(n.finished())
        self.assertEqual(str(n), "~(a&b)")

    def test_not_not_breakdown(self):
        n = ls.Not(ls.Not(ls.Value("a")))
        self.assertEqual(str(n), "~~a")
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 1)
        self.assertEqual(len(vals[0]), 1)
        self.assertEqual(str(vals[0][0]), "a")

    def test_not_and_breakdown(self):
        n = ls.Not(ls.And(ls.Value("a"), ls.Value("b")))
        self.assertEqual(str(n), "~(a&b)")
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 2)
        self.assertEqual(len(vals[0]), 1)
        self.assertEqual(str(vals[0][0]), "~a")
        self.assertEqual(str(vals[1][0]), "~b")

    def test_not_or_breakdown(self):
        n = ls.Not(ls.Or(ls.Value("a"), ls.Value("b")))
        self.assertEqual(str(n), "~(a|b)")
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 1)
        self.assertEqual(len(vals[0]), 2)
        self.assertEqual(str(vals[0][0]), "~a")
        self.assertEqual(str(vals[0][1]), "~b")

    def test_not_implies_breakdown(self):
        n = ls.Not(ls.Implies(ls.Value("a"), ls.Value("b")))
        self.assertEqual(str(n), "~(a$b)")
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 1)
        self.assertEqual(len(vals[0]), 2)
        self.assertEqual(str(vals[0][0]), "a")
        self.assertEqual(str(vals[0][1]), "~b")

    def test_not_iff_breakdown(self):
        n = ls.Not(ls.Iff(ls.Value("a"), ls.Value("b")))
        self.assertEqual(str(n), "~(a%b)")
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 2)
        self.assertEqual(len(vals[0]), 2)
        self.assertEqual(str(vals[0][0]), "a")
        self.assertEqual(str(vals[0][1]), "~b")
        self.assertEqual(str(vals[1][0]), "~a")
        self.assertEqual(str(vals[1][1]), "b")

    def test_and(self):
        n = ls.And(ls.Value("a"), ls.Value("b"))
        self.assertEqual(str(n), "a&b")
        self.assertFalse(n.finished())
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 1)
        self.assertEqual(len(vals[0]), 2)
        self.assertEqual(str(vals[0][0]), "a")
        self.assertEqual(str(vals[0][1]), "b")

    def test_or(self):
        n = ls.Or(ls.Value("a"), ls.Value("b"))
        self.assertEqual(str(n), "a|b")
        self.assertFalse(n.finished())
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 2)
        self.assertEqual(len(vals[0]), 1)
        self.assertEqual(str(vals[0][0]), "a")
        self.assertEqual(str(vals[1][0]), "b")

    def test_implies(self):
        n = ls.Implies(ls.Value("a"), ls.Value("b"))
        self.assertEqual(str(n), "a$b")
        self.assertFalse(n.finished())
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 2)
        self.assertEqual(len(vals[0]), 1)
        self.assertEqual(str(vals[0][0]), "~a")
        self.assertEqual(str(vals[1][0]), "b")

    def test_iff(self):
        n = ls.Iff(ls.Value("a"), ls.Value("b"))
        self.assertEqual(str(n), "a%b")
        vals, _ = n.breakdown()
        self.assertEqual(len(vals), 2)
        self.assertEqual(len(vals[0]), 2)
        self.assertEqual(str(vals[0][0]), "a")
        self.assertEqual(str(vals[0][1]), "b")
        self.assertEqual(str(vals[1][0]), "~a")
        self.assertEqual(str(vals[1][1]), "~b")

    def test_string_creation(self):
        n = ls.And(ls.Not(ls.Implies(ls.Value("a"), ls.Not(ls.Value("b")))), ls.Iff(ls.Or(ls.Value("c"), ls.Value("d")), ls.Value("a")))
        self.assertEqual(str(n), "(~(a$(~b)))&((c|d)%a)")
