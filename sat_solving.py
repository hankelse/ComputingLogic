"""
solver.py

Provides SAT-based reasoning utilities and the Argument.solve() interface.

- Converts CNF WFFs into PySAT clauses
- Checks validity of arguments via satisfiability
- Returns countermodels for invalid arguments
"""

from pysat.solvers import Glucose3
from itertools import chain
from typing import Tuple, Dict, List

from WFFs.cnfWFFs import CnfWFF
from constants import AND, OR, NOT


# ==========================================================
# --- CNF → PySAT clause conversion helpers ---
# ==========================================================

def _make_varmap() -> Tuple[Dict[str, int], List[int]]:
    """Create a variable map and a counter for new symbol IDs."""
    return {}, [1]


def _get_var(symbol: str, varmap: Dict[str, int], counter: List[int]) -> int:
    """Get integer ID for a symbol, allocating if unseen."""
    if symbol not in varmap:
        varmap[symbol] = counter[0]
        counter[0] += 1
    return varmap[symbol]


def cnf_to_clauses(cnf: CnfWFF) -> Tuple[List[List[int]], Dict[str, int]]:
    """
    Convert a CnfWFF into PySAT-compatible clauses (list of list of ints).
    Each clause = disjunction of literals.
    """
    varmap, counter = _make_varmap()
    clauses: List[List[int]] = []

    def literal_to_int(lit: str) -> int:
        """Convert literal string (e.g. '~P') → signed int."""
        if lit.startswith(f"{NOT}"):
            sym = lit[1:]
            return -_get_var(sym, varmap, counter)
        return _get_var(lit, varmap, counter)

    # Flatten CNF to list of clauses
    clause_lists = cnf.get_clauses()  # e.g. [['~A', 'B'], ['C', '~D']]
    for clause in clause_lists:
        clauses.append([literal_to_int(l) for l in clause])

    return clauses, varmap


# ==========================================================
# --- SAT solving ---
# ==========================================================

def solve_cnf(cnf: CnfWFF) -> Tuple[bool, Dict[str, bool]]:
    """
    Solves a CNF WFF using Glucose3.
    Returns:
        (is_satisfiable, model_dict)
    """
    clauses, varmap = cnf_to_clauses(cnf)

    solver = Glucose3()
    for c in clauses:
        solver.add_clause(c)

    is_sat = solver.solve()
    if not is_sat:
        return False, {}

    model = solver.get_model()
    invmap = {v: k for k, v in varmap.items()}
    named_model = {invmap[abs(l)]: (l > 0) for l in model if abs(l) in invmap}

    return True, named_model


# ==========================================================
# --- Argument Solver Interface ---
# ==========================================================


def solve_argument(cnf_wff: CnfWFF):
    """
    Solves a CNF WFF that represents (Premises ∧ ¬Conclusion).
    
    Returns:
        (is_valid, counterexample)
        
    The argument is valid ⇔ (Premises ∧ ¬Conclusion) is unsatisfiable.
    """

    # --- Step 1: Get clauses directly from CNF WFF ---
    clauses = cnf_wff.get_clauses()  # Each clause is a list of literals like ["~P", "Q"]

    # --- Step 2: Convert literals into CNF node form (for PySAT solver) ---
    def lit_to_cnf(lit: str) -> CnfWFF:
        if lit.startswith(NOT):
            return CnfWFF(operator=NOT, operands=[CnfWFF(atom=lit[1:])])
        return CnfWFF(atom=lit)

    clause_nodes = []
    for clause in clauses:
        lits = [lit_to_cnf(l) for l in clause]
        if len(lits) == 1:
            clause_nodes.append(lits[0])
        else:
            clause_nodes.append(CnfWFF(operator=OR, operands=lits))

    # --- Step 3: Combine clauses into one CNF conjunction ---
    flat_cnf = CnfWFF(operator=AND, operands=clause_nodes)

    # --- Step 4: Solve with SAT solver ---
    is_sat, model = solve_cnf(flat_cnf)

    # --- Step 5: Interpret results ---
    is_valid = not is_sat
    counterexample = model if is_sat else None

    return is_valid, counterexample
