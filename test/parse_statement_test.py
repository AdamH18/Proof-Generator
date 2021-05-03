import unittest
import src.argument_parser as ap


class ParseStatementTest(unittest.TestCase):
    def test_parse_statement_simple(self):
        n = ap.parse_statement("B | C")
        self.assertEqual(str(n), "B|C")

    def test_parse_statement_precedence(self):
        n = ap.parse_statement("A % B $ C | D & ! E")
        self.assertEqual(str(n), "A%(B$(C|(D&(~E))))")

    def test_parse_statement_order(self):
        n = ap.parse_statement("A & B & C & D & E")
        self.assertEqual(str(n), "(((A&B)&C)&D)&E")

    def test_parse_statement_complex(self):
        n = ap.parse_statement("(!(A | B) % (A & C))")
        self.assertEqual(str(n), "(~(A|B))%(A&C)")

    def test_parse_statement_empty(self):
        try:
            ap.parse_statement("")
        except ValueError:
            return
        self.assertEqual(True, False)

    def test_parse_statement_missing_paren(self):
        try:
            ap.parse_statement("A & (B | C")
        except ValueError:
            return
        self.assertEqual(True, False)

    def test_parse_statement_bad_parens(self):
        try:
            ap.parse_statement("A (& B |) C")
        except ValueError:
            return
        self.assertEqual(True, False)

    def test_parse_statement_missing_val(self):
        try:
            ap.parse_statement("A & ")
        except ValueError:
            return
        self.assertEqual(True, False)
