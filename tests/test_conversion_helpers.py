import unittest
from WFFs.strictWFFs import StrictWFF, string_to_WFF


from WFFs.WFF_conversion import (
    eliminate_implications,
    eliminate_xor,
    eliminate_double_negation,
    demorgans,
    distribute_or_over_and,
    convert_to_cnf_wff,
    strict_to_cnf
)

# For readability in expected outputs
AND = "∧"
OR = "∨"
NOT = "~"


class TestEliminateImplications(unittest.TestCase):

    def test_simple_implication(self):
        wff = string_to_WFF("(P→Q)")
        result = eliminate_implications(wff)
        expected = string_to_WFF("(~P∨Q)")
        self.assertEqual(repr(result), repr(expected))

    def test_nested_implications(self):
        wff = string_to_WFF("((P→Q)→R)")
        result = eliminate_implications(wff)
        expected = string_to_WFF("(~(~P∨Q)∨R)")
        self.assertEqual(repr(result), repr(expected))


class TestEliminateXor(unittest.TestCase):

    def test_basic_xor(self):
        wff = string_to_WFF("(P⊕Q)")
        result = eliminate_xor(wff)
        expected = string_to_WFF("((P∨Q)∧~(P∧Q))")
        self.assertEqual(repr(result), repr(expected))

    def test_nested_xor(self):
        wff = string_to_WFF("((P⊕Q)⊕R)")
        result = eliminate_xor(wff)
        # The structure is large; just assert the top operator and substructure
        self.assertEqual(result.operator, AND)
        self.assertIn(OR, (result.operand1.operator, result.operand2.operator))


class TestEliminateDoubleNegation(unittest.TestCase):

    def test_double_negation(self):
        wff = string_to_WFF("~~P")
        result = eliminate_double_negation(wff)
        expected = string_to_WFF("P")
        self.assertEqual(repr(result), repr(expected))

    def test_nested_double_negation(self):
        wff = string_to_WFF("~~~P")
        result = eliminate_double_negation(wff)
        expected = string_to_WFF("~P")
        self.assertEqual(repr(result), repr(expected))

    def test_double_negation_within_complex(self):
        wff = string_to_WFF("((~~P)∧Q)")
        result = eliminate_double_negation(wff)
        expected = string_to_WFF("(P∧Q)")
        self.assertEqual(repr(result), repr(expected))


class TestDeMorgans(unittest.TestCase):

    def test_demorgans_on_and(self):
        wff = string_to_WFF("~(P∧Q)")
        result = demorgans(wff)
        expected = string_to_WFF("((~P)∨(~Q))")
        self.assertEqual(repr(result), repr(expected))

    def test_demorgans_on_or(self):
        wff = string_to_WFF("~(P∨Q)")
        result = demorgans(wff)
        expected = string_to_WFF("((~P)∧(~Q))")
        self.assertEqual(repr(result), repr(expected))

    def test_double_negation_cleared(self):
        wff = string_to_WFF("~~P")
        result = demorgans(wff)
        expected = string_to_WFF("P")
        self.assertEqual(repr(result), repr(expected))


class TestDistributeOrOverAnd(unittest.TestCase):

    def test_simple_distribution_left(self):
        # A ∨ (Q ∧ R) → (A ∨ Q) ∧ (A ∨ R)
        wff = string_to_WFF("(P∨(Q∧R))")
        result = distribute_or_over_and(wff)
        expected = string_to_WFF("((P∨Q)∧(P∨R))")
        self.assertEqual(repr(result), repr(expected))

    def test_simple_distribution_right(self):
        # (Q ∧ R) ∨ B → (Q ∨ B) ∧ (R ∨ B)
        wff = string_to_WFF("((Q∧R)∨P)")
        result = distribute_or_over_and(wff)
        expected = string_to_WFF("((Q∨P)∧(R∨P))")
        self.assertEqual(repr(result), repr(expected))

    def test_no_distribution_needed(self):
        # P ∨ Q (no AND to distribute)
        wff = string_to_WFF("(P∨Q)")
        result = distribute_or_over_and(wff)
        expected = string_to_WFF("(P∨Q)")
        self.assertEqual(repr(result), repr(expected))



class TestToCnf(unittest.TestCase):

    def test_simple_cnf_no_change(self):
        wff = string_to_WFF("(P∧Q)")
        result = convert_to_cnf_wff(wff)
        expected = string_to_WFF("(P∧Q)")
        self.assertEqual(repr(result), repr(expected))

    def test_or_over_and(self):
        wff = string_to_WFF("(P∨(Q∧R))")
        result = convert_to_cnf_wff(wff)
        expected = string_to_WFF("((P∨Q)∧(P∨R))")
        self.assertEqual(repr(result), repr(expected))

    def test_nested_or_over_and(self):
        wff = string_to_WFF("((P∨Q)∨(R∧S))")
        result = convert_to_cnf_wff(wff)
        expected = string_to_WFF("(((P∨Q∨R)∧(P∨Q∨S)))")
        self.assertTrue("∧" in repr(result))


class TestFullCNFPipeline(unittest.TestCase):

    def test_implication_to_cnf(self):
        wff = string_to_WFF("(P→Q)")
        cnf = strict_to_cnf(wff)
        expected = string_to_WFF("(~P∨Q)")
        self.assertEqual(repr(cnf), repr(expected))

    def test_xor_to_cnf(self):
        wff = string_to_WFF("(P⊕Q)")
        cnf = strict_to_cnf(wff)
        self.assertIn("∧", repr(cnf))
        self.assertIn("∨", repr(cnf))

    def test_complex_formula(self):
        wff = string_to_WFF("~((P→Q)∨(R∧S))")
        cnf = strict_to_cnf(wff)
        # Expect a conjunction at top-level after full CNF conversion
        self.assertEqual(cnf.operator, "∧")


if __name__ == "__main__":
    unittest.main(verbosity=0)
