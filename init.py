from get_data import get_folio_data, relabel_folio_data, reshape_data
from testing import run_tests
from pprint import pprint
from constants import VALID, INVALID, NOT, OR, AND, IMPLIES
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




def main():
    # Get foilio data
    f_data = get_folio_data()

    # Format data
    arguments, labels, maps = reshape_data(f_data)

    # Relabel maps
    labels = relabel_folio_data(labels)

    # Test argument
    premises = [
        "a", str(NOT+"b"), str("a"+OR+"b"), str(NOT+"a"+OR+"c"), str(NOT+"a"+AND+"c"), str(NOT+"a"+IMPLIES+"c"), 
        (f"({NOT}a {OR} b) {IMPLIES} {NOT} (a {AND} {NOT} c)")
    ]
    conclusion = "c"
    argument = (premises, conclusion)

    for p in premises[3:]:
        print(p, "-->", end="")
        p = WFF(p)
        print(p)

        print("True:", p.made_true())
        print("False:", p.made_false())

        



    
main()