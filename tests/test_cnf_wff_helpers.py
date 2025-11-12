import unittest
from cnfWFFs import CnfWFF, CONJUNCTIVE_WFF, DISJUNCTIVE_WFF
from constants import AND, OR, NOT, ATOMIC_WFF, UNARY_WFF


class TestAtomicAndUnary(unittest.TestCase):

    def test_atomic_creation(self):
        p = CnfWFF(atom="P")
        self.assertEqual(p.type, ATOMIC_WFF)
        self.assertEqual(repr(p), "P")
        self.assertEqual(p.get_literals(), ["P"])
        self.assertEqual(p.get_clauses(), [["P"]])

    def test_unary_creation(self):
        p = CnfWFF(atom="P")
        not_p = CnfWFF(operator=NOT, operands=[p])
        self.assertEqual(not_p.type, UNARY_WFF)
        self.assertEqual(repr(not_p), "~P")
        self.assertEqual(not_p.get_literals(), ["~P"])
        self.assertEqual(not_p.get_clauses(), [["~P"]])

    def test_invalid_unary_on_non_atomic(self):
        p = CnfWFF(atom="P")
        q = CnfWFF(atom="Q")
        bad_inner = CnfWFF(operator=OR, operands=[p, q])
        with self.assertRaises(AssertionError):
            CnfWFF(operator=NOT, operands=[bad_inner])


class TestDisjunctive(unittest.TestCase):

    def test_two_operands(self):
        p = CnfWFF(atom="P")
        q = CnfWFF(atom="Q")
        clause = CnfWFF(operator=OR, operands=[p, q])
        self.assertEqual(clause.type, DISJUNCTIVE_WFF)
        self.assertEqual(repr(clause), "(P ∨ Q)")
        self.assertEqual(clause.get_literals(), ["P", "Q"])
        self.assertEqual(clause.get_clauses(), [["P", "Q"]])

    def test_three_operands(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        clause = CnfWFF(operator=OR, operands=[p, q, r])
        self.assertEqual(repr(clause), "(P ∨ Q ∨ R)")
        self.assertEqual(len(clause.operands), 3)
        self.assertEqual(clause.get_literals(), ["P", "Q", "R"])

    def test_nested_or_flattening(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        inner = CnfWFF(operator=OR, operands=[q, r])
        outer = CnfWFF(operator=OR, operands=[p, inner])
        # Flattened automatically
        self.assertEqual(len(outer.operands), 3)
        self.assertEqual(outer.get_literals(), ["P", "Q", "R"])

    def test_invalid_or_operand(self):
        p = CnfWFF(atom="P")
        # Attempt to double-negate (invalid)
        with self.assertRaises(AssertionError):
            bad = CnfWFF(operator=NOT, operands=[CnfWFF(operator=NOT, operands=[p])])



class TestConjunctive(unittest.TestCase):

    def test_two_clauses(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        clause1 = CnfWFF(operator=OR, operands=[p, q])
        clause2 = CnfWFF(operator=OR, operands=[r, q])
        cnf = CnfWFF(operator=AND, operands=[clause1, clause2])
        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        self.assertEqual(repr(cnf), "((P ∨ Q) ∧ (R ∨ Q))")
        self.assertEqual(cnf.get_clauses(), [["P", "Q"], ["R", "Q"]])

    def test_three_clauses(self):
        p, q, r, s = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R"), CnfWFF(atom="S")
        c1 = CnfWFF(operator=OR, operands=[p, q])
        c2 = CnfWFF(atom="R")
        c3 = CnfWFF(atom="S")
        cnf = CnfWFF(operator=AND, operands=[c1, c2, c3])
        self.assertEqual(len(cnf.operands), 3)
        self.assertEqual(cnf.get_clauses(), [["P", "Q"], ["R"], ["S"]])

    def test_nested_and_flattening(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        c1 = CnfWFF(operator=OR, operands=[p, q])
        c2 = CnfWFF(operator=OR, operands=[q, r])
        inner = CnfWFF(operator=AND, operands=[c1, c2])
        outer = CnfWFF(operator=AND, operands=[inner, c1])
        # should flatten automatically
        self.assertEqual(len(outer.operands), 3)
        self.assertEqual(outer.get_clauses(), [["P", "Q"], ["Q", "R"], ["P", "Q"]])

    def test_and_with_literals_is_valid(self):
        p = CnfWFF(atom="P")
        not_p = CnfWFF(operator=NOT, operands=[p])
        q = CnfWFF(atom="Q")
        cnf = CnfWFF(operator=AND, operands=[q, not_p])
        self.assertEqual(cnf.type, "conjunctive_wff")
        self.assertEqual(cnf.get_clauses(), [["Q"], ["~P"]])


class TestFlattening(unittest.TestCase):

    def test_flatten_conjunctions(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        c1 = CnfWFF(operator=OR, operands=[p, q])
        c2 = CnfWFF(operator=OR, operands=[r, p])
        cnf = CnfWFF(operator=AND, operands=[c1, c2])
        flat = cnf.flatten_conjunctions()
        self.assertEqual(len(flat), 2)
        self.assertTrue(all(isinstance(c, CnfWFF) for c in flat))

    def test_flatten_disjunctions(self):
        p, q, r = CnfWFF(atom="P"), CnfWFF(atom="Q"), CnfWFF(atom="R")
        inner = CnfWFF(operator=OR, operands=[q, r])
        outer = CnfWFF(operator=OR, operands=[p, inner])
        flat = outer.flatten_disjunctions()
        self.assertEqual(len(flat), 3)
        self.assertEqual([f.atom for f in flat], ["P", "Q", "R"])


class TestComplexStructures(unittest.TestCase):

    def test_large_cnf(self):
        # ((~P ∨ Q ∨ R) ∧ (S ∨ ~T ∨ U) ∧ V)
        P, Q, R, S, T, U, V = [CnfWFF(atom=x) for x in "PQRSTUV"]
        notP = CnfWFF(operator=NOT, operands=[P])
        notT = CnfWFF(operator=NOT, operands=[T])

        clause1 = CnfWFF(operator=OR, operands=[notP, Q, R])
        clause2 = CnfWFF(operator=OR, operands=[S, notT, U])
        cnf = CnfWFF(operator=AND, operands=[clause1, clause2, V])

        self.assertEqual(cnf.type, CONJUNCTIVE_WFF)
        self.assertEqual(len(cnf.operands), 3)
        self.assertEqual(
            cnf.get_clauses(),
            [["~P", "Q", "R"], ["S", "~T", "U"], ["V"]],
        )
        self.assertIn("∧", repr(cnf))
        self.assertIn("∨", repr(cnf))


if __name__ == "__main__":
    unittest.main(verbosity=2)
