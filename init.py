from get_data import get_folio_data, relabel_folio_data
from testing import run_tests
from pprint import pprint
from constants import VALID, INVALID
import itertools



def reshape_data(dataset):
    X = [(d["premises"], d["conclusion"]) for d in dataset]
    y = [d["label"] for d in dataset]
    maps = [d["map"] for d in dataset]
    return X, y, maps


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

    # Get solver
    algo = lambda premises, conclusion : VALID

    #Run tests
    run_tests(algo, arguments, labels)

    
main()