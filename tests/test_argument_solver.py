# import unittest
# from constants import VALID, INVALID, AND, OR, NOT, IMPLIES
# from argument import Argument
# from sat_solving import solve_argument
# from WFFs.cnfWFFs import CnfWFF
# from WFFs.strictWFFs import StrictWFF
# from WFFs.WFF_conversion import strict_to_cnf


# class TestStrictToCNFNegation(unittest.TestCase):
#     """Tests for negating complex CNFs through StrictWFF conversion."""

#     def test_negation_of_conjunction(self):
#         wff = StrictWFF(operator=AND,
#                         operand1=StrictWFF(atom="P"),
#                         operand2=StrictWFF(atom="Q"))
#         neg = StrictWFF(operator=NOT, operand1=wff)
#         cnf = strict_to_cnf(neg)
#         # ¬(P ∧ Q) → (¬P ∨ ¬Q)
#         clauses = cnf.get_clauses()
#         self.assertIn([f"{NOT}P", f"{NOT}Q"], clauses)

#     def test_negation_of_disjunction(self):
#         wff = StrictWFF(operator=OR,
#                         operand1=StrictWFF(atom="A"),
#                         operand2=StrictWFF(atom="B"))
#         neg = StrictWFF(operator=NOT, operand1=wff)
#         cnf = strict_to_cnf(neg)
#         # ¬(A ∨ B) → (¬A ∧ ¬B)
#         clauses = cnf.get_clauses()
#         self.assertTrue(
#             any(f"{NOT}A" in c or f"{NOT}B" in c for c in clauses),
#             msg=f"Expected {NOT}A or {NOT}B in clauses, got {clauses}"
# )

#     def test_negation_of_nested_expression(self):
#         inner = StrictWFF(operator=IMPLIES,
#                           operand1=StrictWFF(atom="A"),
#                           operand2=StrictWFF(atom="B"))
#         wff = StrictWFF(operator=AND,
#                         operand1=inner,
#                         operand2=StrictWFF(atom="C"))
#         neg = StrictWFF(operator=NOT, operand1=wff)
#         cnf = strict_to_cnf(neg)
#         # Should contain (¬A ∨ ¬C ∨ ¬B) style clauses
#         flat = [lit for clause in cnf.get_clauses() for lit in clause]
#         self.assertTrue(any(NOT in lit for lit in flat))


# class TestCnfToClauses(unittest.TestCase):
#     """Tests for CNF flattening into SAT solver clauses."""

#     def setUp(self):
#         self.P = CnfWFF(atom="P")
#         self.Q = CnfWFF(atom="Q")
#         self.R = CnfWFF(atom="R")

#     def test_single_disjunction_to_clauses(self):
#         cnf = CnfWFF(operator=OR, operands=[self.P, self.Q])
#         clauses, varmap = cnf.get_clauses(), {"P": 1, "Q": 2}
#         self.assertIn(["P", "Q"], clauses)

#     def test_conjunction_of_two_disjunctions(self):
#         disj1 = CnfWFF(operator=OR, operands=[self.P, self.Q])
#         disj2 = CnfWFF(operator=OR, operands=[self.R, self.Q])
#         cnf = CnfWFF(operator=AND, operands=[disj1, disj2])
#         all_clauses = cnf.get_clauses()
#         self.assertEqual(len(all_clauses), 2)
#         self.assertTrue(all(isinstance(c, list) for c in all_clauses))

#     def test_negated_literal_is_atomic(self):
#         negP = CnfWFF(operator=NOT, operands=[self.P])
#         clauses = negP.get_clauses()
#         self.assertEqual(clauses, [[f"{NOT}P"]])


# class TestArgumentSolver(unittest.TestCase):
#     """Tests full Argument.solve() validity checks."""

#     def test_simple_valid_argument(self):
#         # P → Q, P ⊢ Q
#         premises = ["P → Q", "P"]
#         conclusion = "Q"
#         arg = Argument(premises, conclusion)
#         cnf_arg = arg.to_cnf()
#         is_valid, _ = cnf_arg.solve()
#         self.assertTrue(is_valid)

#     def test_simple_invalid_argument(self):
#         # Q, ⊢ P  (invalid)
#         premises = ["Q"]
#         conclusion = "P"
#         arg = Argument(premises, conclusion)
#         cnf_arg = arg.to_cnf()
#         is_valid, model = cnf_arg.solve()
#         self.assertFalse(is_valid)
#         self.assertIsInstance(model, dict)
#         self.assertTrue("Q" in model or "P" in model)

#     def test_xor_in_premise(self):
#         # (P ⊕ Q), P ⊢ ¬Q (valid)
#         premises = ["(P ⊕ Q)", "P"]
#         conclusion = f"{NOT}Q"
#         arg = Argument(premises, conclusion)
#         arg.expand_quantifiers([])  # no effect, but check stability
#         cnf_arg = arg.to_cnf()
#         valid, _ = cnf_arg.solve()
#         self.assertTrue(valid)

#     def test_double_negation_elimination(self):
#         # ¬¬P ⊢ P (valid)
#         arg = Argument([f"{NOT}{NOT}P"], "P")
#         cnf_arg = arg.to_cnf()
#         is_valid, _ = cnf_arg.solve()
#         self.assertTrue(is_valid, f"Cnf arg was {cnf_arg}")

#     def test_demorgan_distribution_validity(self):
#         # ¬(P ∧ Q) ⊢ ¬P ∨ ¬Q (valid)
#         premises = [f"{NOT}(P {AND} Q)"]
#         conclusion = f"{NOT}P {OR} {NOT}Q"
#         arg = Argument(premises, conclusion)
#         cnf_arg = arg.to_cnf()

#         print("\n============================")
#         print("ARGUMENT UNDER TEST:")
#         print("  Premises:", [repr(p) for p in cnf_arg.premises])
#         print("  Conclusion:", repr(cnf_arg.conclusion))

#         all_clauses = []
#         for p in cnf_arg.premises:
#             all_clauses.extend(p.get_clauses())
#         neg_conc = cnf_arg.conclusion.negate()
#         print("  Negated Conclusion CNF:", repr(neg_conc))
#         all_clauses.extend(neg_conc.get_clauses())

#         print("  CNF Clauses Sent to Solver:")
#         for c in all_clauses:
#             print("   ", c)

#         is_valid, model = cnf_arg.solve()

#         print("  SAT Solver Result:")
#         print("   is_valid =", is_valid)
#         print("   model =", model)

#         self.assertTrue(is_valid, msg="Expected valid argument, got invalid.")

#     def test_quantified_argument_expansion_and_solve(self):
#         # ∀x(P(x) → Q(x)), P(a) ⊢ Q(a)
#         premises = ["∀x(Px → Qx)", "Pa"]
#         conclusion = "Qa"
#         arg = Argument(premises, conclusion)
#         arg.expand_quantifiers(["a"])
#         cnf_arg = arg.to_cnf()
#         is_valid, _ = cnf_arg.solve()
#         self.assertTrue(is_valid)

#     def test_negated_conclusion_distribution(self):
#         # Check that ¬(A ∧ B) is handled via De Morgan correctly in solve()
#         premises = ["A ∧ B"]
#         conclusion = "A"
#         arg = Argument(premises, conclusion)
#         cnf_arg = arg.to_cnf()
#         valid, model = cnf_arg.solve()
#         self.assertTrue(valid)


# class TestEndToEndFolioCompatibility(unittest.TestCase):
#     """Sanity check with data samples from the FOLIO-like dataset."""

#     def test_batch_processing_simulation(self):
#         arguments = [
#             (["P → Q", "Q → R", "P"], "R"),       # valid
#             ([f"P → Q", f"{NOT}Q"], f"{NOT}P"),    # valid (contrapositive)
#             (["P → Q", "Q"], "P"),                 # invalid
#         ]
#         expected = [VALID, VALID, INVALID]

#         for (premises, conclusion), label in zip(arguments, expected):
#             arg = Argument(premises, conclusion)
#             cnf = arg.to_cnf()
#             is_valid, _ = cnf.solve()
#             computed = VALID if is_valid else INVALID
#             self.assertEqual(computed, label)


# if __name__ == "__main__":
#     unittest.main(verbosity=2)
