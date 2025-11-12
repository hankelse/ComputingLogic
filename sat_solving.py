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
        if lit.startswith("~"):
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

def solve_argument(argument):
    """Checks validity by testing satisfiability of (Premises ∧ ¬Conclusion)."""
    cnf_argument = argument.to_cnf() if argument.is_strict() else argument
    premises = cnf_argument.premises
    conclusion = cnf_argument.conclusion
    neg_conclusion = conclusion.negate()

    # --- Step 2: Collect CNF clauses ---
    clauses = []
    for p in premises:
        clauses.extend(p.get_clauses())
    clauses.extend(neg_conclusion.get_clauses())

    # --- Step 3: Helper for literals ---
    def lit_to_cnf(lit: str) -> CnfWFF:
        return CnfWFF(operator=NOT, operands=[CnfWFF(atom=lit[1:])]) if lit.startswith("~") else CnfWFF(atom=lit)

    # --- Step 4: Build CNF structure ---
    argument_cnf_operands = []
    for clause in clauses:
        lits = [lit_to_cnf(lit) for lit in clause]
        if len(lits) == 1:
            argument_cnf_operands.append(lits[0])
        else:
            argument_cnf_operands.append(CnfWFF(operator=OR, operands=lits))

    argument_cnf = CnfWFF(operator=AND, operands=argument_cnf_operands)

    # --- Step 5: Solve with PySAT ---
    is_sat, model = solve_cnf(argument_cnf)

    # --- Step 6: Interpret result ---
    is_valid = not is_sat
    counterexample = model if is_sat else None
    return is_valid, counterexample
