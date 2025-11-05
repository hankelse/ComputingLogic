from get_data import get_folio_data, relabel_folio_data, reshape_data
from testing import run_tests
from pprint import pprint
from constants import VALID, INVALID, NOT, OR, AND, IMPLIES
import itertools
from WFF import WFF
from cnf import to_cnf


def make_varmap():
    """Create a new variable mapping with counter state."""
    return {}, [1]  # varmap, counter


def get_var(symbol: str, varmap: dict, counter: list) -> int:
    """Return an integer id for a symbol, allocating if needed."""
    if symbol not in varmap:
        varmap[symbol] = counter[0]
        counter[0] += 1
    return varmap[symbol]

from WFF import WFF, ATOMIC_WFF, UNARY_WFF, BINARY_WFF
from constants import AND, OR, NOT

def wff_to_clauses(wff: WFF, varmap: dict, counter: list) -> list[list[int]]:
    """
    Convert a CNF WFF into a list of clauses (list of lists of ints).
    """
    if wff.type == ATOMIC_WFF:
        return [[get_var(wff.string, varmap, counter)]]

    if wff.type == UNARY_WFF and wff.main_operator == NOT:
        child = wff.operands[0]
        if child.type != ATOMIC_WFF:
            raise ValueError("CNF should only have negation on atoms")
        return [[-get_var(child.string, varmap, counter)]]

    if wff.main_operator == OR:
        left = wff_to_clauses(wff.operands[0], varmap, counter)
        right = wff_to_clauses(wff.operands[1], varmap, counter)
        return [left[0] + right[0]]

    if wff.main_operator == AND:
        left = wff_to_clauses(wff.operands[0], varmap, counter)
        right = wff_to_clauses(wff.operands[1], varmap, counter)
        return left + right

    raise ValueError(f"Unexpected node in CNF: {wff}")



from cnf import to_cnf

def cnf_clauses_from_wff(wff: WFF):
    """
    Convert any WFF into CNF clauses for a SAT solver.
    """
    # Step 1: convert to CNF form
    cnf_wff = to_cnf(wff)

    # Step 2: allocate variable map
    varmap, counter = make_varmap()

    # Step 3: flatten to clauses
    clauses = wff_to_clauses(cnf_wff, varmap, counter)

    return clauses, varmap

# --- Convert CNF WFF to PySAT format ---
def cnf_to_clauses(wff, varmap=None, counter=None):
    from WFF import ATOMIC_WFF, UNARY_WFF, BINARY_WFF
    from constants import AND, OR, NOT

    if varmap is None:
        varmap = {}
    if counter is None:
        counter = [1]

    def get_var(symbol):
        if symbol not in varmap:
            varmap[symbol] = counter[0]
            counter[0] += 1
        return varmap[symbol]

    # --- Base case: Atomic ---
    if wff.type == ATOMIC_WFF:
        return [[get_var(wff.string)]], varmap

    # --- Negation ---
    # if wff.type == UNARY_WFF and wff.main_operator == NOT:
    #     child = wff.operands[0]
    #     return [[-get_var(repr(child))]], varmap
    if wff.type == UNARY_WFF and wff.main_operator == NOT:
        child = wff.operands[0]
        if child.type != ATOMIC_WFF:
            raise ValueError("CNF should only have negation on atoms")
        return [[-get_var(child.string)]], varmap

    # --- OR (disjunction) ---
    if wff.main_operator == OR:
        left_clauses, varmap = cnf_to_clauses(wff.operands[0], varmap, counter)
        right_clauses, varmap = cnf_to_clauses(wff.operands[1], varmap, counter)
        return [left_clauses[0] + right_clauses[0]], varmap

    # --- AND (conjunction) ---
    if wff.main_operator == AND:
        left_clauses, varmap = cnf_to_clauses(wff.operands[0], varmap, counter)
        right_clauses, varmap = cnf_to_clauses(wff.operands[1], varmap, counter)
        return left_clauses + right_clauses, varmap

    raise ValueError("Unexpected structure in CNF")



from pysat.solvers import Glucose3

def solve_cnf_clauses(clauses: list[list[int]], varmap: dict):
    """
    Solve a CNF given as clauses with PySAT.
    Returns (is_sat, model_as_dict).
    """
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    is_sat = solver.solve()
    if not is_sat:
        return False, None

    model = solver.get_model()

    # invert varmap for readability
    invmap = {v: k for k, v in varmap.items()}
    named_model = {invmap[abs(lit)]: (lit > 0) for lit in model if abs(lit) in invmap}

    return True, named_model

def solve_with_sat(wff: WFF):
    """
    Convert a WFF into CNF, flatten to clauses, solve with PySAT.
    """
    clauses, varmap = cnf_clauses_from_wff(wff)
    return solve_cnf_clauses(clauses, varmap)


# FROM WFFS

from constants import AND, NOT
from WFF import WFF
from cnf import to_cnf
from pysat.solvers import Glucose3

# --- Helper to join premises into a single WFF ---
def join_with_and(wffs):
    """Combine a list of WFFs into one big conjunction."""
    if not wffs:
        return None
    result = wffs[0]
    for w in wffs[1:]:
        result = WFF(None, from_WFF=True, main_operator=AND, operands=[result, w])
    return result


# --- Build Premises ∧ ¬Conclusion ---
def build_argument_wff(premises, conclusion):
    premises_wffs = [WFF(p) for p in premises]
    conclusion_wff = WFF(conclusion)
    premises_conj = join_with_and(premises_wffs)

    not_conclusion = WFF(None, from_WFF=True, main_operator=NOT, operands=[conclusion_wff])

    if premises_conj:
        return WFF(None, from_WFF=True, main_operator=AND, operands=[premises_conj, not_conclusion])
    else:
        return not_conclusion
    
# def check_argument_validity(premises, conclusion):
    arg_wff = build_argument_wff(premises, conclusion)
    cnf_wff = to_cnf(arg_wff)
    clauses, varmap = cnf_to_clauses(cnf_wff), {}

    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    if solver.solve():
        model = solver.get_model()
        named_model = decode_model(model, varmap)
        return False, named_model  # invalid, counterexample
    else:
        return True, None  # valid
    

from pysat.solvers import Glucose3

def check_argument_validity(arg_wff):
    """
    Given a single WFF representing (premises ∧ ¬conclusion),
    determines whether the argument is valid using a SAT solver.
    Returns:
        (is_valid, model, decoded_model)
    """

    # --- Convert to CNF ---
    cnf_wff = to_cnf(arg_wff)
    # print(f"CNF Form: {cnf_wff}")

    clauses, varmap = cnf_to_clauses(cnf_wff)

    

    # --- Initialize solver ---
    solver = Glucose3()
    for clause in clauses:
        solver.add_clause(clause)

    # --- Solve ---
    sat = solver.solve()

    if sat:
        # Argument is INVALID
        model = solver.get_model()          # list of ints, e.g. [1, -2, 3]
        decoded = decode_model(model, varmap)  # dict like {'A': True, 'B': False}
        return False, model, decoded
    else:
        # Argument is VALID
        return True, None, None




# # --- Main loop over arguments ---
# def check_all_arguments(arguments):
#     results = []
#     for premises, conclusion in arguments:
#         is_valid, model = check_argument_validity(premises, conclusion)
#         results.append((premises, conclusion, is_valid, model))
#     return results




# # --- Main loop over arguments ---
# def check_all_arguments(arguments):
#     results = []
#     for premises, conclusion in arguments:
#         is_valid, model = check_argument_validity(premises, conclusion)
#         results.append((premises, conclusion, is_valid, model))
#     return results


def decode_model(model, varmap):
    """
    Convert a PySAT model (list of ints) into a dict of {varname: truth}.
    """
    invmap = {v: k for k, v in varmap.items()}
    assignment = {}
    for lit in model:
        if abs(lit) in invmap:
            assignment[invmap[abs(lit)]] = (lit > 0)
    return assignment



def main():
    # Get foilio data
    f_data = get_folio_data()

    # Format data
    arguments, labels, maps = reshape_data(f_data)

    # Relabel maps
    labels = relabel_folio_data(labels)

    results = check_all_arguments(arguments)
    for premises, conclusion, valid, model in results:
        print("Premises:", premises, "| Conclusion:", conclusion)
        print("Valid?", valid)
        if not valid:
            print("Counterexample:", model)
        print()


    # expr = WFF("(a → (b ∨ c))")
    # is_sat, model = solve_with_sat(expr)

    # print("SAT?:", is_sat)
    # print("Model:", model)




# main() 