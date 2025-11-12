'''
A Type of WFF where 
- Any operator is allowed
- WFFs must be binary, unary, atomic, or have a quantifier
'''

# from __future__ import annotations
from typing import Optional, Literal, Union

from copy import deepcopy

from constants import QuantifierType, OperatorType, UnaryOperator, BinaryOperator, ATOMIC_WFF, UNARY_WFF, BINARY_WFF, QUANTIFIER_WFF
from constants import UNARY_OPERATORS, BINARY_OPERATORS, UNIVERSAL_Q, EXISTENTIAL_Q, AND, OR



class StrictWFF: pass
class StrictWFF:
    """
    A type of WFF where:
    - Any operator is allowed
    - Each WFF is one of: atomic, unary, binary, or quantified
    """

    def __init__(self,
                atom: Optional[str] = None,
                operator: Optional[str] = None,
                operand1: Optional[StrictWFF] = None,
                operand2: Optional[StrictWFF] = None,
                quantifier: Optional[tuple[QuantifierType, str]] = None):
        self.atom = atom
        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2
        self.quantifier = quantifier


        self.type = self.assign_and_enforce_type()
        
    def __repr__(self) -> str:
            """
            Returns a readable, recursive string representation of this WFF.
            Handles all four WFF types: atomic, unary, binary, quantified.
            """

            # --- Atomic ---
            if self.type == ATOMIC_WFF:
                return self.atom or "⊥"

            # --- Unary ---
            elif self.type == UNARY_WFF:
                # ensure proper parentheses for clarity
                return f"({self.operator}{repr(self.operand1)})"

            # --- Binary ---
            elif self.type == BINARY_WFF:
                # fully parenthesized infix representation
                return f"({repr(self.operand1)} {self.operator} {repr(self.operand2)})"

            # --- Quantified ---
            elif self.type == QUANTIFIER_WFF:
                quant, var = self.quantifier
                return f"{quant}{var}({repr(self.operand1)})"

            # --- Unknown ---
            return "⊥"

    def assign_and_enforce_type(self):
        """
        Given the inputs at construction, 
        returns the type and 
        asserts that there is no missing information or extra information provided
        """

        # Atomic WFF
        if self.atom:
            assert self.operator is None, "Atomic WFFs cannot have an operator."
            assert self.operand1 is None, "Atomic WFFs cannot have operands."
            assert self.operand2 is None, "Atomic WFFs cannot have operands."
            assert self.quantifier is None, "Atomic WFFs cannot have a quantifier."
            return ATOMIC_WFF

        # Quantified WFF
        if self.quantifier:
            assert self.operator is None, "Quantified WFFs cannot have an operator."
            assert self.operand2 is None, "Quantified WFFs cannot have a second operand."
            assert self.operand1 is not None, "Quantified WFFs must have a body (operand1)."
            return QUANTIFIER_WFF

        # Must be unary or binary if not atomic or quantified
        assert self.operator is not None, "Non-atomic WFFs must have an operator."
        assert self.operand1 is not None, "Non-atomic WFFs must have at least one operand."

        # Binary WFF
        if self.operand2 is not None:
            assert self.operator in BINARY_OPERATORS, (
                f"Binary WFFs must have an operator in {BinaryOperator}, "
                f"got '{self.operator}'."
            )
            return BINARY_WFF

        # Unary WFF
        else:
            assert self.operator in UNARY_OPERATORS, (
                f"Unary WFFs must have an operator in {UnaryOperator}, "
                f"got '{self.operator}'."
            )
            return UNARY_WFF
    
    def get_domain(self) -> list[str]:
        """Collects all lowercase atoms in this WFF recursively."""
        if hasattr(self, "domain") and self.domain:
            return self.domain

        if self.type == ATOMIC_WFF:
            return only_lowercase(repr(self))

        domains = []
        if self.operand1:
            domains += self.operand1.get_domain()
        if self.operand2:
            domains += self.operand2.get_domain()

        return list(set(domains))
    
    def expand_quantifiers(self, domain: list[str]) -> None:
        """
        Recursively expands all quantifiers in this StrictWFF
        into finite conjunctions (∀) or disjunctions (∃)
        over the given domain of constants.
        """
    

        # --- Step 1: Recurse on operands first ---
        if self.type in (UNARY_WFF, BINARY_WFF):
            if self.operand1:
                self.operand1.expand_quantifiers(domain)
            if self.operand2:
                self.operand2.expand_quantifiers(domain)

        # --- Step 2: Expand quantifier at this node ---
        if not self.quantifier:
            return

        symbol, variable = self.quantifier

        if symbol == UNIVERSAL_Q:
            join_op = AND
        elif symbol == EXISTENTIAL_Q:
            join_op = OR
        else:
            raise ValueError(f"Unknown quantifier: {symbol}")

        # Create copies of the body with variable replaced by each domain constant
        new_wffs = []
        for const in domain:
            if const == variable: continue

            wff_copy = deepcopy(self.operand1)  # body of quantifier
            wff_copy.replace(variable, const)
            wff_copy.quantifier = None
            new_wffs.append(wff_copy)

        # --- Join all copies with the appropriate operator ---
        # --- Join all copies with the appropriate operator ---
        if not new_wffs:
            return  # no domain to expand into, skip expansion
        joined = list_to_StrictWFF(new_wffs, join_op)

        # Mutate this node into the joined WFF
        self.operator = joined.operator
        self.operand1 = joined.operand1
        self.operand2 = joined.operand2
        self.quantifier = None
        self.type = joined.type

    def replace(self, to_replace, replacer):
        """Recursively replace variable names in atomic strings."""
        if self.type == ATOMIC_WFF:
            if self.atom and to_replace in self.atom:
                self.atom = self.atom.replace(to_replace, replacer)

        elif self.type == UNARY_WFF:
            if self.operand1:
                self.operand1.replace(to_replace, replacer)

        elif self.type == BINARY_WFF:
            if self.operand1:
                self.operand1.replace(to_replace, replacer)
            if self.operand2:
                self.operand2.replace(to_replace, replacer)

        elif self.type == QUANTIFIER_WFF:
            if self.operand1:
                self.operand1.replace(to_replace, replacer)

            

def list_to_StrictWFF(wff_list: list[StrictWFF], operator: str) -> StrictWFF:
        """
        Given a list of WFFs and a binary operator, 
        joins them recursively into a single StrictWFF tree.
        """
        if not wff_list:
            raise ValueError("Cannot join empty WFF list.")
        if len(wff_list) == 1:
            return wff_list[0]

        head = wff_list[0]
        rest = list_to_StrictWFF(wff_list[1:], operator)
        return StrictWFF(operator=operator, operand1=head, operand2=rest)

# ==== String Parsing Helper Functions ==== #

def string_to_WFF(s: str) -> StrictWFF:
    """
    Parse a logical formula string into a StrictWFF.
    Supports quantifiers, unary and binary operators, and atomic propositions.
    """

    s = strip_outer_parentheses(s.replace(" ", ""))
    if not s:
        raise ValueError("Cannot parse empty string into WFF.")

    # --- Handle quantifier ---
    if len(s) >= 2 and s[0] in ("∀", "∃") and s[1].isalpha():
        quant = (s[0], s[1])  # e.g. ('∀', 'x')
        body_str = s[2:]
        body_str = strip_outer_parentheses(body_str)
        return StrictWFF(quantifier=quant, operand1=string_to_WFF(body_str))

    # --- Find main operator ---
    main_op = find_main_operator(s)

    # --- Atomic ---
    if main_op is None:
        return StrictWFF(atom=s)

    # --- Unary ---
    if main_op in {"~"}:
        idx = s.index(main_op)
        operand_str = s[idx + 1:]
        return StrictWFF(operator=main_op, operand1=string_to_WFF(operand_str))

    # --- Binary ---
    # Find operator index at depth 0 (important for nested parentheses)
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and ch == main_op:
            left_str = s[:i]
            right_str = s[i + 1:]
            return StrictWFF(
                operator=main_op,
                operand1=string_to_WFF(left_str),
                operand2=string_to_WFF(right_str),
            )

    # If we somehow didn’t return earlier:
    raise ValueError(f"Could not parse WFF: {s}")

def strip_outer_parentheses(s: str) -> str:
    """Removes one layer of wrapping parentheses if they enclose the entire string."""
    s = s.strip()
    if not s:
        return s

    if s[0] not in ("(", "[") or s[-1] not in (")", "]"):
        return s

    depth = 0
    for i, ch in enumerate(s):
        if ch in "([": 
            depth += 1
        elif ch in ")]":
            depth -= 1
            if depth == 0 and i != len(s) - 1:
                return s  # outer () don’t wrap entire string
    return s[1:-1]  # remove outermost layer

def find_main_operator(s: str) -> Optional[str]:
    """
    Finds the main (outermost) operator at depth 0.
    Treats quantifiers as operators too.
    """
    s = s.strip()
    if not s:
        return None

    # Quantifiers as main operator if appear at beginning
    if len(s) >= 2 and s[0] in ("∀", "∃") and s[1].isalpha():
        return s[0]  # quantifier symbol

    # Normal operator search
    depth = 0
    found_unary = None

    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0:
            if ch in BINARY_OPERATORS:
                return ch
            elif ch in UNARY_OPERATORS and found_unary is None:
                found_unary = ch
    return found_unary


# === Random Helpers === #

def only_lowercase(str):
    result = ""
    for char in str:
        if char.islower():
            result += char
    return result        
