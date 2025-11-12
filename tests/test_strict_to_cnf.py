import unittest
from strictWFFs import StrictWFF
from cnfWFFs import CnfWFF, CONJUNCTIVE_WFF, DISJUNCTIVE_WFF
from constants import AND, OR, NOT, ATOMIC_WFF, UNARY_WFF, BINARY_WFF
from WFF_conversion import strict_to_cnf, convert_to_cnf_wff  # your file/module name here

# These helper functions must exist in the same namespace:
# eliminate_implications, eliminate_xor, eliminate_double_negation,
# demorgans, distribute_or_over_and


class TestConvertToCnfWff(unittest.TestCase):
    """Unit tests for the direct StrictWFF → CnfWFF structural conversion."""

    def test_atomic_conversion(self):
        p = StrictWFF(atom="P")
        cnf = convert_to_cnf_wff(p)
        self.assertIsInstance(cnf, CnfWFF)
        self.assertEqual(cnf.atom, "P")
        self.assertEqual(cnf.type, ATOMIC_WFF)
        self.assertEqual(repr(cnf), "P")

    def test_unary_conversion(self):
        p = StrictWFF(atom="P")
        not_p = StrictWFF(operator=NOT, operand1=p)
        cnf = convert_to_cnf_wff(not_p)
        self.assertEqual(cnf.type, UNARY_WFF)
        self.assertEqual(repr(cnf), "~P")
        self.assertEqual(cnf.get_literals(), ["~P"])

    def test_binary_and_conversion(self):
        p, q = StrictWFF(atom="P"), StrictWFF(atom="Q")
        expr = StrictWFF(operator=AND, operand1=p, operand2=q)
        cnf = convert_to_cnf_wff(expr)
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        self.assertEqual(repr(cnf), "(P ∧ Q)")
        self.assertEqual(cnf.get_clauses(), [["P"], ["Q"]])

    def test_binary_or_conversion(self):
        p, q = StrictWFF(atom="P"), StrictWFF(atom="Q")
        expr = StrictWFF(operator=OR, operand1=p, operand2=q)
        cnf = convert_to_cnf_wff(expr)
        self.assertEqual(cnf.type, DISJUNCTIVE_WFF)
        self.assertEqual(repr(cnf), "(P ∨ Q)")
        self.assertEqual(cnf.get_clauses(), [["P", "Q"]])

    def test_invalid_binary_operator(self):
        p, q = StrictWFF(atom="P"), StrictWFF(atom="Q")
        expr = StrictWFF(operator="→", operand1=p, operand2=q)
        with self.assertRaises(ValueError):
            convert_to_cnf_wff(expr)

    def test_invalid_type_raises(self):
        with self.assertRaises(AssertionError):
            _ = StrictWFF(atom=None, operator=None, operand1=None)


class TestStrictToCnf(unittest.TestCase):
    """End-to-end tests for the full CNF normalization pipeline."""

    def test_eliminate_implication(self):
        # P → Q should become (~P ∨ Q)
        expr = StrictWFF(operator="→",
                         operand1=StrictWFF(atom="P"),
                         operand2=StrictWFF(atom="Q"))
        cnf = strict_to_cnf(expr)
        self.assertEqual(repr(cnf), "(~P ∨ Q)")
        self.assertEqual(cnf.get_clauses(), [["~P", "Q"]])

    def test_eliminate_xor(self):
        # (P ⊕ Q) = ((P ∨ Q) ∧ ¬(P ∧ Q))
        expr = StrictWFF(operator="⊕",
                         operand1=StrictWFF(atom="P"),
                         operand2=StrictWFF(atom="Q"))
        cnf = strict_to_cnf(expr)
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        clauses = cnf.get_clauses()
        literals = [sorted(c) for c in clauses]
        self.assertTrue(any("P" in c and "Q" in c for c in literals))

    def test_double_negation_elimination(self):
        # ~~P -> P
        p = StrictWFF(atom="P")
        double = StrictWFF(operator=NOT,
                           operand1=StrictWFF(operator=NOT, operand1=p))
        cnf = strict_to_cnf(double)
        self.assertEqual(repr(cnf), "P")

    def test_demorgan_push_negation(self):
        # ¬(P ∨ Q) -> (~P ∧ ~Q)
        p, q = StrictWFF(atom="P"), StrictWFF(atom="Q")
        expr = StrictWFF(operator=NOT,
                         operand1=StrictWFF(operator=OR, operand1=p, operand2=q))
        cnf = strict_to_cnf(expr)
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        self.assertEqual(cnf.get_clauses(), [["~P"], ["~Q"]])

    def test_distribution_or_over_and(self):
        # (P ∨ (Q ∧ R)) -> ((P ∨ Q) ∧ (P ∨ R))
        p, q, r = StrictWFF(atom="P"), StrictWFF(atom="Q"), StrictWFF(atom="R")
        expr = StrictWFF(operator=OR,
                         operand1=p,
                         operand2=StrictWFF(operator=AND, operand1=q, operand2=r))
        cnf = strict_to_cnf(expr)
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        clauses = [sorted(c) for c in cnf.get_clauses()]
        self.assertIn(sorted(["P", "Q"]), clauses)
        self.assertIn(sorted(["P", "R"]), clauses)

    def test_complex_nested_formula(self):
        # (P → Q) ∧ ¬(R ∨ S)
        expr = StrictWFF(
            operator=AND,
            operand1=StrictWFF(operator="→",
                               operand1=StrictWFF(atom="P"),
                               operand2=StrictWFF(atom="Q")),
            operand2=StrictWFF(operator=NOT,
                               operand1=StrictWFF(operator=OR,
                                                  operand1=StrictWFF(atom="R"),
                                                  operand2=StrictWFF(atom="S")))
        )
        cnf = strict_to_cnf(expr)
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        clauses = cnf.get_clauses()
        self.assertIn(["~P", "Q"], clauses)
        self.assertIn(["~R"], clauses)
        self.assertIn(["~S"], clauses)

    def test_deeply_nested_formula_stays_flat(self):
        # ((((P ∨ Q) ∨ R) ∨ S) ∨ T)
        p, q, r, s, t = [StrictWFF(atom=x) for x in "PQRST"]
        nested = StrictWFF(operator=OR, operand1=p, operand2=q)
        for atom in [r, s, t]:
            nested = StrictWFF(operator=OR, operand1=nested, operand2=atom)
        cnf = strict_to_cnf(nested)
        self.assertEqual(cnf.type, DISJUNCTIVE_WFF)
        lits = cnf.get_literals()
        self.assertCountEqual(lits, ["P", "Q", "R", "S", "T"])

    def test_invalid_operator_in_pipeline(self):
        # After normalization, any invalid operator should raise
        p, q = StrictWFF(atom="P"), StrictWFF(atom="Q")
        with self.assertRaises((AssertionError, ValueError)):
            expr = StrictWFF(operator="⊗", operand1=p, operand2=q)
            strict_to_cnf(expr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
