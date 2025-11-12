import unittest

from argument import Argument
from WFFs.strictWFFs import StrictWFF, string_to_WFF
from WFFs.cnfWFFs import CnfWFF
from WFFs.WFF_conversion import strict_to_cnf
from constants import AND, OR, NOT


class TestArgumentInitialization(unittest.TestCase):
    """
    Tests for Argument construction from strings, StrictWFFs, and CnfWFFs.
    Ensures proper normalization, error handling, and string representation.
    """

    def test_create_from_strings(self):
        """Should parse strings into StrictWFFs and store them as premises/conclusion."""
        arg = Argument(
            premises=["P→Q", "P"],
            conclusion="Q"
        )
        self.assertEqual(arg._form_type, "strict")
        self.assertEqual(len(arg.premises), 2)
        self.assertIsInstance(arg.premises[0], StrictWFF)
        self.assertIsInstance(arg.conclusion, StrictWFF)
        self.assertIn("⊢", repr(arg))

    def test_create_from_strictWFF_objects(self):
        """Should accept StrictWFFs directly."""
        p1 = string_to_WFF("P→Q")
        p2 = string_to_WFF("P")
        c = string_to_WFF("Q")
        arg = Argument([p1, p2], c)
        self.assertEqual(arg._form_type, "strict")
        self.assertTrue(all(isinstance(p, StrictWFF) for p in arg.premises))

    def test_create_from_cnfWFF_objects(self):
        """Should accept CNFWFFs directly."""
        p1 = CnfWFF(operator=OR, operands=[CnfWFF(atom="~P"), CnfWFF(atom="Q")])
        p2 = CnfWFF(atom="P")
        c = CnfWFF(atom="Q")
        arg = Argument([p1, p2], c)
        self.assertEqual(arg._form_type, "cnf")
        self.assertTrue(all(isinstance(p, CnfWFF) for p in arg.premises))

    def test_mixed_types_raises_error(self):
        """Mixing StrictWFF and CnfWFF should raise a TypeError."""
        p1 = string_to_WFF("P")
        p2 = CnfWFF(atom="Q")
        with self.assertRaises(TypeError):
            Argument([p1, p2], CnfWFF(atom="R"))

    def test_empty_premises_raises_error(self):
        """An Argument must have at least one premise."""
        with self.assertRaises(ValueError):
            Argument([], "P")

    def test_invalid_input_type_raises(self):
        """Passing an unsupported object type should raise a TypeError."""
        with self.assertRaises(TypeError):
            Argument([42, "P"], "Q")

    def test_repr_output(self):
        """Ensure __repr__ gives readable argument representation."""
        arg = Argument(["P→Q", "P"], "Q")
        repr_str = repr(arg)
        self.assertIn("⊢", repr_str)
        self.assertIn("P", repr_str)
        self.assertIn("Q", repr_str)


class TestQuantifierExpansion(unittest.TestCase):
    """
    Tests for expanding quantifiers in arguments containing StrictWFFs.
    """

    def test_expand_universal_quantifier(self):
        """∀x(P(x) → Q(x)), P(a) ⊢ Q(a) should expand into conjunctions over the domain."""
        arg = Argument(["∀x(P(x)→Q(x))", "P(a)"], "Q(a)")
        arg.expand_quantifiers(domain=["a", "b"])
        repr_str = repr(arg)
        self.assertIn("a", repr_str)
        self.assertIn("b", repr_str)
        self.assertIn("→", repr_str)

    def test_expand_existential_quantifier(self):
        """∃xP(x) should expand into a disjunction over domain."""
        arg = Argument(["∃xP(x)"], "P(a)")
        arg.expand_quantifiers(domain=["a", "b"])
        repr_str = repr(arg)
        self.assertTrue(("∨" in repr_str) or ("V" in repr_str))

    def test_expand_quantifiers_on_cnf_raises(self):
        """Expanding quantifiers on CNF arguments should raise TypeError."""
        p1 = CnfWFF(operator=OR, operands=[CnfWFF(atom="P"), CnfWFF(atom="Q")])
        p2 = CnfWFF(atom="P")
        c = CnfWFF(atom="Q")
        arg = Argument([p1, p2], c)
        with self.assertRaises(TypeError):
            arg.expand_quantifiers(["a", "b"])


class TestCNFConversion(unittest.TestCase):
    """
    Tests for converting StrictWFF-based arguments into CNF form.
    """

    def test_basic_cnf_conversion(self):
        """(P→Q), P ⊢ Q should yield CNF form with (~P∨Q)."""
        arg = Argument(["P→Q", "P"], "Q")
        cnf_arg = arg.to_cnf()

        self.assertEqual(cnf_arg._form_type, "cnf")
        self.assertTrue(all(isinstance(p, CnfWFF) for p in cnf_arg.premises))
        repr_str = repr(cnf_arg)
        self.assertIn("∨", repr_str)
        self.assertIn("~P", repr_str)
        self.assertIn("Q", repr_str)

    def test_cnf_conversion_preserves_conclusion(self):
        """Conclusion should also be converted to CNF form."""
        arg = Argument(["P→Q"], "P∨R")
        cnf_arg = arg.to_cnf()
        self.assertIsInstance(cnf_arg.conclusion, CnfWFF)

    def test_cnf_conversion_idempotent(self):
        """Calling to_cnf() on an already-CNF Argument should return itself."""
        p1 = CnfWFF(operator=OR, operands=[CnfWFF(atom="~P"), CnfWFF(atom="Q")])
        p2 = CnfWFF(atom="P")
        c = CnfWFF(atom="Q")
        arg = Argument([p1, p2], c)
        same = arg.to_cnf()
        self.assertIs(arg, same)

    def test_nested_disjunction_distribution(self):
        """Check that nested OR inside AND is distributed properly in CNF conversion."""
        arg = Argument(["P∨(Q∧R)"], "P")
        cnf_arg = arg.to_cnf()
        clauses = [sorted(c) for p in cnf_arg.premises for c in p.get_clauses()]
        self.assertIn(sorted(["P", "Q"]), clauses)
        self.assertIn(sorted(["P", "R"]), clauses)


class TestUtilityMethods(unittest.TestCase):
    """
    Tests for smaller helper methods like get_all_atoms and __repr__ formatting.
    """

    def test_get_all_atoms_strict(self):
        """get_all_atoms() should return lowercase domain constants/variables for strict arguments."""
        arg = Argument(["P(a)→Q(b)", "R(x)"], "Q(b)")
        atoms = arg.get_all_atoms()
        self.assertCountEqual(atoms, ["a", "b", "x"])

    def test_get_all_atoms_cnf(self):
        """get_all_atoms() should work for CNF arguments."""
        p1 = CnfWFF(operator=OR, operands=[CnfWFF(atom="~P"), CnfWFF(atom="Q")])
        p2 = CnfWFF(atom="R")
        c = CnfWFF(atom="Q")
        arg = Argument([p1, p2], c)
        atoms = arg.get_all_atoms()
        self.assertCountEqual(atoms, ["P", "Q", "R"])

    def test_repr_includes_all_premises(self):
        """Ensure the __repr__ lists all premises with commas and the turnstile."""
        arg = Argument(["P", "Q", "R"], "S")
        repr_str = repr(arg)
        self.assertTrue(repr_str.count(",") == 2)
        self.assertIn("⊢", repr_str)


class TestErrorConditions(unittest.TestCase):
    """
    Test edge cases and explicit failure modes.
    """

    def test_to_cnf_on_mixed_types_raises(self):
        """Attempting to convert mixed-type argument should fail at init."""
        p1 = string_to_WFF("P")
        p2 = CnfWFF(atom="Q")
        with self.assertRaises(TypeError):
            Argument([p1, p2], "Q")

    def test_expand_quantifiers_without_domain(self):
        """If expand_quantifiers is called with an empty domain, result should be no-op."""
        arg = Argument(["∀xP(x)"], "P(a)")
        arg.expand_quantifiers(domain=[])
        self.assertIn("∀x", repr(arg))  # should remain unchanged


if __name__ == "__main__":
    unittest.main(verbosity=2)
