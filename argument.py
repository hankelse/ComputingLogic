'''
A class for arguments, the main class interacted with from users
'''

# argument.py
from typing import List, Union
from WFFs.strictWFFs import StrictWFF, string_to_WFF
from WFFs.cnfWFFs import CnfWFF
from WFFs.WFF_conversion import strict_to_cnf
from sat_solving import solve_argument



class Argument:
    """
    Represents a logical argument consisting of 1+ premises and 1 conclusion.
    
    Supports:
      - Initialization from strings, StrictWFFs, or CnfWFFs
      - Quantifier expansion (if using StrictWFFs)
      - Conversion to CNF form
    """

    def __init__(self, premises: List[Union[str, StrictWFF, CnfWFF]], conclusion: Union[str, StrictWFF, CnfWFF]):
        if not premises:
            raise ValueError("Argument must have at least one premise.")

        # --- Normalize all inputs ---
        self.premises = [self._normalize(p) for p in premises]
        self.conclusion = self._normalize(conclusion)

        # --- Determine representation type ---
        premise_types = {type(p) for p in self.premises}
        premise_types.add(type(self.conclusion))

        if premise_types == {StrictWFF}:
            self._form_type = "strict"
        elif premise_types == {CnfWFF}:
            self._form_type = "cnf"
        else:
            raise TypeError("All formulas in an Argument must be either all StrictWFF or all CnfWFF.")
    
    def solve(self) -> tuple[bool, dict]:
        """
        Uses PySAT to determine if the argument is valid.
        Returns:
            (is_valid, model)
        - is_valid: True if argument is logically valid (premises entail conclusion)
        - model: counterexample (dict) if invalid
        """
        return solve_argument(self)
    
    # ==========================================================
    # --- Internal type checking ---
    # ==========================================================

    def is_strict(self) -> bool:
        """Returns True if this argument contains StrictWFF objects."""
        return self._form_type == "strict"

    def is_cnf(self) -> bool:
        """Returns True if this argument contains CnfWFF objects."""
        return self._form_type == "cnf"

    # ==========================================================
    # --- Internal normalization helper ---
    # ==========================================================

    def _normalize(self, item: Union[str, StrictWFF, CnfWFF]) -> Union[StrictWFF, CnfWFF]:
        """Converts strings to StrictWFFs, leaves others as-is."""
        if isinstance(item, StrictWFF) or isinstance(item, CnfWFF):
            return item
        elif isinstance(item, str):
            return string_to_WFF(item)
        else:
            raise TypeError(f"Invalid formula type: {type(item)}")

    # ==========================================================
    # --- Operations ---
    # ==========================================================

    def expand_quantifiers(self, domain: List[str]) -> None:
        """
        Expands all quantifiers in premises and conclusion (if StrictWFFs).
        Mutates the internal formulas.
        """
        if self._form_type != "strict":
            raise TypeError("Quantifier expansion only applies to StrictWFF arguments.")

        for p in self.premises:
            p.expand_quantifiers(domain)
        self.conclusion.expand_quantifiers(domain)

    def to_cnf(self) -> "Argument":
        """
        Converts all StrictWFFs into CNFWFFs.
        Returns a new Argument in CNF form.
        """
        if self._form_type == "cnf":
            return self  # already CNF

        cnf_premises = [strict_to_cnf(p) for p in self.premises]
        cnf_conclusion = strict_to_cnf(self.conclusion)
        return Argument(cnf_premises, cnf_conclusion)

    
    # ==========================================================
    # --- Representation ---
    # ==========================================================

    def __repr__(self) -> str:
        premise_strs = [repr(p) for p in self.premises]
        return f"{', '.join(premise_strs)} ⊢ {repr(self.conclusion)}"

    # ==========================================================
    # --- Utility ---
    # ==========================================================

    def get_all_atoms(self) -> List[str]:
        """
        Returns all logical symbols referenced in the argument.
        - For StrictWFFs: returns lowercase domain constants/variables.
        - For CnfWFFs: returns predicate symbols (negations removed).
        """
        atoms = []
        for p in self.premises + [self.conclusion]:
            if isinstance(p, CnfWFF):
                # get_literals returns strings like "~P" or "Q"
                lits = p.get_literals()
                for lit in lits:
                    # strip negation symbol if present
                    lit = lit.lstrip("~")
                    # if predicate has arguments, remove "(...)" part
                    if "(" in lit:
                        lit = lit[:lit.index("(")]
                    atoms.append(lit)
            else:
                # strict form: lowercase constants/variables
                atoms.extend(p.get_domain())

        return sorted(set(atoms))

