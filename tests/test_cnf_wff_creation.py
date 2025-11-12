import unittest
from cnfWFFs import CnfWFF, CONJUNCTIVE_WFF, DISJUNCTIVE_WFF
from constants import AND, OR, NOT, ATOMIC_WFF, UNARY_WFF


class TestCNFDepthAndStructure(unittest.TestCase):

    # ----------------------------------------------------------
    # ✅ VALID CNF CONSTRUCTIONS (depth <= 4)
    # ----------------------------------------------------------

    def test_depth_1_atomic(self):
        p = CnfWFF(atom="P")
        self.assertEqual(p.type, ATOMIC_WFF)
        self.assertEqual(repr(p), "P")

    def test_depth_2_unary(self):
        p = CnfWFF(atom="P")
        not_p = CnfWFF(operator=NOT, operands=[p])
        self.assertEqual(not_p.type, UNARY_WFF)
        self.assertEqual(repr(not_p), "~P")

    def test_depth_3_disjunction_of_literals(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        not_q = CnfWFF(operator=NOT, operands=[q])
        clause = CnfWFF(operator=OR, operands=[p, not_q, r])
        self.assertEqual(clause.type, DISJUNCTIVE_WFF)
        self.assertEqual(len(clause.operands), 3)
        self.assertEqual(clause.get_literals(), ["P", "~Q", "R"])

    def test_depth_4_conjunction_of_clauses(self):
        p, q, r, s = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R"), CnfWFF(atom="S")
        not_p = CnfWFF(operator=NOT, operands=[p])
        clause1 = CnfWFF(operator=OR, operands=[p, q])
        clause2 = CnfWFF(operator=OR, operands=[r, not_p, s])
        cnf = CnfWFF(operator=AND, operands=[clause1, clause2])
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        self.assertEqual(len(cnf.operands), 2)
        self.assertEqual(cnf.get_clauses(), [["P", "Q"], ["R", "~P", "S"]])

    # ----------------------------------------------------------
    # ✅ DEPTH IS CONTROLLED BY FLATTENING (NO ASSERTION)
    # ----------------------------------------------------------

    def test_depth_5_nested_disjunction_is_flattened(self):
        # Build (((P ∨ Q) ∨ R) ∨ S) ∨ T — should flatten automatically
        p, q, r, s, t = [CnfWFF(atom=x) for x in "PQRST"]
        clause1 = CnfWFF(operator=OR, operands=[p, q])
        clause2 = CnfWFF(operator=OR, operands=[clause1, r])
        clause3 = CnfWFF(operator=OR, operands=[clause2, s, t])
        self.assertEqual(clause3.type, DISJUNCTIVE_WFF)
        # Flattened: 5 atoms in one disjunction
        self.assertEqual(len(clause3.operands), 5)

    def test_depth_5_nested_conjunction_is_flattened(self):
        # ((((A ∧ B) ∧ C) ∧ D) ∧ E) should flatten automatically
        a, b, c, d, e = [CnfWFF(atom=x) for x in "ABCDE"]
        conj1 = CnfWFF(operator=AND, operands=[a, b])
        conj2 = CnfWFF(operator=AND, operands=[conj1, c])
        conj3 = CnfWFF(operator=AND, operands=[conj2, d, e])
        self.assertEqual(conj3.type, CONJUNCTIVE_WFF)
        # Flattened: 5 operands in one conjunction
        self.assertEqual(len(conj3.operands), 5)

    # ----------------------------------------------------------
    # ❌ INVALID STRUCTURE (rule violations)
    # ----------------------------------------------------------

    def test_invalid_disjunction_contains_conjunction(self):
        p, q = CnfWFF(atom="P"), CnfWFF(atom="Q")
        inner = CnfWFF(operator=AND, operands=[p, q])
        with self.assertRaises(AssertionError):
            CnfWFF(operator=OR, operands=[inner, p])

    def test_invalid_negation_on_non_atomic(self):
        p, q = CnfWFF(atom="P"), CnfWFF(atom="Q")
        clause = CnfWFF(operator=OR, operands=[p, q])
        with self.assertRaises(AssertionError):
            CnfWFF(operator=NOT, operands=[clause])

    # ----------------------------------------------------------
    # ✅ AUTO-FLATTENING BEHAVIOR
    # ----------------------------------------------------------

    def test_auto_flatten_disjunction(self):
        # (P ∨ (Q ∨ R) ∨ S) should become (P ∨ Q ∨ R ∨ S)
        p, q, r, s = [CnfWFF(atom=x) for x in "PQRS"]
        inner = CnfWFF(operator=OR, operands=[q, r])
        outer = CnfWFF(operator=OR, operands=[p, inner, s])
        self.assertEqual(len(outer.operands), 4)
        self.assertEqual(outer.get_literals(), ["P", "Q", "R", "S"])

    def test_auto_flatten_conjunction(self):
        # ((A ∨ B) ∧ (C)) ∧ (A ∨ B)
        p, q, r = [CnfWFF(atom=x) for x in "PQR"]
        c1 = CnfWFF(operator=OR, operands=[p, q])
        c2 = CnfWFF(atom="R")  # replace single-element disjunction
        inner = CnfWFF(operator=AND, operands=[c1, c2])
        outer = CnfWFF(operator=AND, operands=[inner, c1])
        self.assertEqual(len(outer.operands), 3)
        self.assertEqual(outer.get_clauses(), [["P", "Q"], ["R"], ["P", "Q"]])

    def test_conjunction_with_atomic_literals_allowed(self):
        p = CnfWFF(atom="P")
        not_p = CnfWFF(operator=NOT, operands=[p])
        q = CnfWFF(atom="Q")
        cnf = CnfWFF(operator=AND, operands=[q, not_p])
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        self.assertEqual(cnf.get_clauses(), [["Q"], ["~P"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
