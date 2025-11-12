'''
A class for arguments, the main class interacted with from users
'''

# argument.py
from typing import List, Union
from WFFs.strictWFFs import StrictWFF, string_to_WFF, list_to_StrictWFF
from WFFs.cnfWFFs import CnfWFF
from WFFs.WFF_conversion import strict_to_cnf
from sat_solving import solve_argument

from constants import AND, NOT



from typing import List, Union
from WFFs.strictWFFs import StrictWFF, string_to_WFF
from WFFs.WFF_conversion import strict_to_cnf
from WFFs.cnfWFFs import CnfWFF
from sat_solving import solve_argument


class Argument:
    """
    Represents a logical argument (premises ⊢ conclusion) in StrictWFF form.

    - Always built from StrictWFFs or strings (never CNFs).
    - Saves a negated copy of the conclusion before CNF conversion.
    - CNF conversion happens via `.to_cnf()` and returns a CNFArgument.
    """

    def __init__(self, premises: List[Union[str, StrictWFF]], conclusion: Union[str, StrictWFF]):
        if not premises:
            raise ValueError("Argument must have at least one premise.")
        
        self._solvable = True

        # --- Always normalize to StrictWFFs ---
        self.premises: List[StrictWFF] = [self._normalize_to_strict(p) for p in premises]
        self.conclusion: StrictWFF = self._normalize_to_strict(conclusion)

        # --- Save negated conclusion (in strict form) ---
        self.negated_conclusion_strict: StrictWFF = StrictWFF(operator=NOT, operand1=self.conclusion)

        # --- Validity WFF: P {AND} {NOT} C
        premises_WFF = list_to_StrictWFF(self.premises, AND)
        self.validity_wff = StrictWFF(operator=AND, operand1=premises_WFF, operand2=self.negated_conclusion_strict)

        self._form_type = "strict"

        self.domain = self.validity_wff.get_domain()
    
    def solvable(self):
        if len(self.domain) <= 1: return False
        return self._solvable

    # ==========================================================
    # --- Solving Interface ---
    # ==========================================================

    def solve(self) -> tuple[bool, dict]:
        """
        Converts to CNF and checks argument validity using SAT.
        """
        cnf_argument = self.to_cnf()
        return solve_argument(cnf_argument)

    # ==========================================================
    # --- Conversion and Expansion ---
    # ==========================================================

    def expand_quantifiers(self) -> None:
        """
        Expands all quantifiers of the validity argument.
        Operates in place).
        """
        
        assert len(self.domain) > 1, f"Can't expand argument with no atoms in domain: domain = {self.domain}"

        self.validity_wff.expand_quantifiers(self.domain)

    def to_cnf(self, debug: bool = False):
        """
        Returns a CNF form of the argument WFF: (Premises ∧ ¬Conclusion)
        """
        print(self.validity_wff)
        cnf = strict_to_cnf(self.validity_wff)
        if debug:
            print("CNF conversion result:")
            for clause in cnf.get_clauses():
                print(" ", clause)
        return cnf

    # ==========================================================
    # --- Internal Helpers ---
    # ==========================================================

    def _normalize_to_strict(self, item: Union[str, StrictWFF]) -> StrictWFF:
        """Parses strings into StrictWFFs, passes StrictWFFs through."""
        if isinstance(item, StrictWFF):
            return item
        elif isinstance(item, str):
            wff = string_to_WFF(item)
            if wff: return wff
            else:
                # No wff was able to be created
                self._solvable = False
                return wff
        else:
            raise TypeError(f"Invalid formula type: {type(item)}")
        
    def form_type(self):
        return "strict"

    # ==========================================================
    # --- Representation ---
    # ==========================================================

    def __repr__(self) -> str:
        prems = ", ".join(repr(p) for p in self.premises)
        return f"{prems} ⊢ {repr(self.conclusion)}"
