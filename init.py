from get_data import get_folio_data, relabel_folio_data, reshape_data
from testing import run_tests
from pprint import pprint
from constants import VALID, INVALID, NOT, OR, AND, IMPLIES, UNIVERSAL_Q, EXISTENTIAL_Q
import itertools
from WFF import WFF

from cnf import to_cnf


def brute_force_validity(premises, conclusion):
    # Collect all atoms (like Aa, Bb, etc.)
    def collect_atoms(expr):
        return set(token for token in expr.replace("(", " ").replace(")", " ").split()
                   if token and token[0].isalpha() and token not in ["∀x", "∃x"])
    
    atoms = set()
    for prem in premises:
        atoms |= collect_atoms(prem)
    atoms |= collect_atoms(conclusion)
    atoms = sorted(atoms)

    # Truth table evaluator
    def eval_expr(expr, valuation):
        # Replace atoms with truth values
        s = expr
        for a in atoms:
            s = s.replace(a, str(valuation[a]))
        # Replace logical symbols with Python equivalents
        s = (s.replace("¬", " not ")
               .replace("∧", " and ")
               .replace("∀", " or ")
               .replace("→", " <= ")  # We'll handle implication separately
               .replace("⊕", " != "))
        # Handle implication manually (since "→" isn't native)
        while "->" in s:  # if you had "->", but your symbols are "→"
            pass
        # Evaluate safely
        return eval(s)

    # Try all valuations
    for values in itertools.product([False, True], repeat=len(atoms)):
        valuation = dict(zip(atoms, values))
        if all(eval_expr(p, valuation) for p in premises):
            if not eval_expr(conclusion, valuation):
                return False  # counterexample found
    return True

from copy import deepcopy
from WFF import list_to_WFF
from WFF import new_WFF
from sat_solving import check_argument_validity


def main():
    # Get foilio data
    f_data = get_folio_data()

    # Format data
    arguments, labels, maps = reshape_data(f_data)

    # Relabel maps
    labels = relabel_folio_data(labels)

    # premises = ["∃x [Cx]", "a", "b", "c"]
    # conclusion = f"∃x Cx"

    # arguments = [(premises, conclusion)]
    for i, arg in enumerate(arguments):
        premises_raw = arg[0]
        conclusion_raw = arg[1]
        print(f"Input: Premises:{premises_raw} Conclusion {conclusion_raw}")

        if any("⊕" in p for p in premises_raw) or "⊕" in conclusion_raw:
            continue


        # --- Convert strings to WFF objects ---
        premises = [WFF(p) for p in premises_raw]
        conclusion = WFF(conclusion_raw)

        print("\n" + "="*60)
        print(f"Argument #{i+1}")
        print("-"*60)
        print("Premises:")
        for p in premises:
            print(f"  {p}")
        print(f"Conclusion: {conclusion}")

        # --- Combine premises into single WFF ---
        premises_WFF = list_to_WFF(premises, AND)
        domain = list(set(premises_WFF.get_domain() + conclusion.get_domain()))

        # if len(domain) == 1: continue

        # print(f"Domain: {domain}")

        # --- Expand quantifiers ---
        premises_WFF.expand_quantifers(domain)
        conclusion.expand_quantifers(domain)
        # print(f"Expanded Premises: {premises_WFF}")
        # print(f"Expanded Conclusion: {conclusion}")

        # --- Build final argument WFF: (Premises ∧ ¬Conclusion) ---
        conclusion_negated = new_WFF(NOT, conclusion)
        argument = new_WFF(AND, premises_WFF, conclusion_negated)
        # print(f"Combined Argument WFF: {argument}")

        # --- Solve using PySAT ---
        is_valid, model, decoded_model = check_argument_validity(argument)

        print("-"*60)
        if is_valid:
            result = VALID
            print("The argument is VALID.")
            print("    No satisfying assignment exists (premises entail conclusion).")
        else:
            result = INVALID
            print("The argument is INVALID.")
            print("    Counterexample:")
            if decoded_model:
                for sym, val in decoded_model.items():
                    print(f"      {sym} = {val}")
            else:
                print("      (No decoded model available)")
        print("="*60 + "\n")

        print(f"{is_valid} corresponds to dataset label: {labels[i]}")
        assert (result == labels[i])

    # for i, arg in enumerate(arguments):
    #     # if i != 19: continue
    #     # print(maps[i])
    #     premises = arg[0]
    #     conclusion = arg[1]

    #     premises = [WFF(p) for p in premises]
    #     conclusion = WFF(conclusion)


    #     print(f"Premises = {premises}")
    #     print(f"Conclusion = {conclusion}")

    #     premises_WFF = list_to_WFF(premises, AND)
    #     domain = list(set(premises_WFF.get_domain() + conclusion.get_domain()))
    #     print(f"Domain = {domain}")


    #     print(f"Combined:", premises_WFF)

    #     premises_WFF.expand_quantifers(domain)
    #     conclusion.expand_quantifers(domain)
    #     print(f"Premises Expanded:", premises_WFF)
    #     print(f"Conclusion Expanded:", conclusion)

    #     # Negate and add conclusion
    #     premises_negated = new_WFF(NOT, premises_WFF)

    #     argument = new_WFF(AND, premises_negated, conclusion)
    #     print(f"Argument = {argument}")


    #     #Solve
    #     # cnf_argument = to_cnf(argument)
    #     # print(f"CNF = {cnf_argument}")


    #     label, assignment = check_argument_validity(argument)
    #     if label:
    #         print(f"The Argument is invalid! \n\t Assignment: {assignment}")
    #     else:
    #         print(f"The Argument is valid    \n\t Assignment: {assignment}")


       
        



        # for p in premises:
        #     pw = WFF(p)
        #     print(f"Premise: {p}      --> {pw}")
        #     pw.expand_quantifers()
        #     print(f"After expanding: {pw}")


    
main()