
from constants import QuantifierType, OperatorType, UnaryOperator, BinaryOperator, ATOMIC_WFF, UNARY_WFF, BINARY_WFF, QUANTIFIER_WFF
from constants import UNARY_OPERATORS, BINARY_OPERATORS, UNIVERSAL_Q, EXISTENTIAL_Q, AND, OR, NOT

from strictWFFs import StrictWFF
from cnfWFFs import CnfWFF


# === Expanding Arguments === #


# === Converting Strict WFFs --> CNF WFFS=== #

def strict_to_cnf(wff: StrictWFF) -> CnfWFF:
    """
    Converts a StrictWFF into CNF form:
    1. Eliminate →
    2. Eliminate ⊕
    3. Eliminate double negations
    4. Push negations inward (De Morgan)
    5. Distribute OR over AND
    """
    step1 = eliminate_implications(wff)
    step2 = eliminate_xor(step1)
    step3 = eliminate_double_negation(step2)
    step4 = demorgans(step3)
    step5 = distribute_or_over_and(step4)

    # Convert to cnf wff
    cnf_wff = convert_to_cnf_wff(step5)


    return cnf_wff

def convert_to_cnf_wff(wff: StrictWFF) -> CnfWFF:
    # Atomic
    if wff.type == ATOMIC_WFF:
        return CnfWFF(atom=wff.atom)

    # Negation
    if wff.type == UNARY_WFF:
        assert wff.operator == NOT, f"Unexpected unary operator in CNF: {wff.operator}"
        inner = convert_to_cnf_wff(wff.operand1)
        return CnfWFF(operator=NOT, operands=[inner])

    # Binary
    if wff.type == BINARY_WFF:
        op = wff.operator
        left = convert_to_cnf_wff(wff.operand1)
        right = convert_to_cnf_wff(wff.operand2)

        if op == AND:
            return CnfWFF(operator=AND, operands=[left, right])
        elif op == OR:
            return CnfWFF(operator=OR, operands=[left, right])
        else:
            raise ValueError(f"Unexpected binary operator in CNF conversion: {op}")

    raise ValueError(f"Unexpected StrictWFF type in CNF conversion: {wff.type}")

def distribute_or_over_and(wff: StrictWFF) -> StrictWFF:
    """Recursively distributes OR over AND to produce CNF."""
    # --- Base cases ---
    if wff.type == ATOMIC_WFF or wff.type == UNARY_WFF:
        return wff

    if wff.operator == AND:
        left = distribute_or_over_and(wff.operand1)
        right = distribute_or_over_and(wff.operand2)
        return StrictWFF(operator=AND, operand1=left, operand2=right)

    if wff.operator == OR:
        left = distribute_or_over_and(wff.operand1)
        right = distribute_or_over_and(wff.operand2)

        # Apply distribution only when needed
        if left.operator == AND:
            # (A ∧ B) ∨ C → (A ∨ C) ∧ (B ∨ C)
            new_left = distribute_or_over_and(
                StrictWFF(operator=OR, operand1=left.operand1, operand2=right)
            )
            new_right = distribute_or_over_and(
                StrictWFF(operator=OR, operand1=left.operand2, operand2=right)
            )
            return StrictWFF(operator=AND, operand1=new_left, operand2=new_right)

        elif right.operator == AND:
            # A ∨ (B ∧ C) → (A ∨ B) ∧ (A ∨ C)
            new_left = distribute_or_over_and(
                StrictWFF(operator=OR, operand1=left, operand2=right.operand1)
            )
            new_right = distribute_or_over_and(
                StrictWFF(operator=OR, operand1=left, operand2=right.operand2)
            )
            return StrictWFF(operator=AND, operand1=new_left, operand2=new_right)

        else:
            # No distribution needed
            return StrictWFF(operator=OR, operand1=left, operand2=right)

    return wff


# Helper functions
def eliminate_implications(wff: StrictWFF) -> StrictWFF:
    """
    Recursively eliminate → and ↔ from a StrictWFF.
    (A → B) becomes (¬A ∨ B)
    (A ↔ B) becomes ((A → B) ∧ (B → A)) → which also expands recursively
    """
    # Atomic or quantified WFFs are unaffected
    if wff.type == ATOMIC_WFF:
        return StrictWFF(atom=wff.atom)
    if wff.type == UNARY_WFF:
        return StrictWFF(operator=wff.operator, operand1=eliminate_implications(wff.operand1))

    # Binary cases
    if wff.type == BINARY_WFF:
        op = wff.operator
        A = eliminate_implications(wff.operand1)
        B = eliminate_implications(wff.operand2)

        # Implication
        if op == "→":
            return StrictWFF(operator="∨", operand1=StrictWFF(operator="~", operand1=A), operand2=B)

        # Biconditional
        elif op == "↔":
            left  = StrictWFF(operator="→", operand1=A, operand2=B)
            right = StrictWFF(operator="→", operand1=B, operand2=A)
            both  = StrictWFF(operator="∧", operand1=left, operand2=right)
            return eliminate_implications(both)  # recurse again to remove → in those

        # Regular binary (∧, ∨, ⊕)
        else:
            return StrictWFF(operator=op, operand1=A, operand2=B)

    raise ValueError(f"Unknown WFF type: {wff.type}")

def eliminate_xor(wff: StrictWFF) -> StrictWFF:
    """
    Recursively eliminate ⊕ (exclusive or) from a StrictWFF.
    (A ⊕ B) becomes ((A ∨ B) ∧ ¬(A ∧ B))
    """
    if wff.type == ATOMIC_WFF:
        return StrictWFF(atom=wff.atom)
    if wff.type == UNARY_WFF:
        return StrictWFF(operator=wff.operator, operand1=eliminate_xor(wff.operand1))

    if wff.type == BINARY_WFF:
        op = wff.operator
        A = eliminate_xor(wff.operand1)
        B = eliminate_xor(wff.operand2)

        # XOR elimination
        if op == "⊕":
            left  = StrictWFF(operator="∨", operand1=A, operand2=B)
            right = StrictWFF(operator="∧", operand1=A, operand2=B)
            not_right = StrictWFF(operator="~", operand1=right)
            return StrictWFF(operator="∧", operand1=left, operand2=not_right)

        # Normal binary
        else:
            return StrictWFF(operator=op, operand1=A, operand2=B)

    raise ValueError(f"Unknown WFF type: {wff.type}")

def eliminate_double_negation(wff: StrictWFF) -> StrictWFF:
    """
    Recursively removes all instances of double negation:
      ¬(¬A)  →  A
    """
    if wff.type == ATOMIC_WFF:
        return StrictWFF(atom=wff.atom)

    if wff.type == UNARY_WFF:
        inner = eliminate_double_negation(wff.operand1)
        # If it's a double negation
        if wff.operator == "~" and inner.type == UNARY_WFF and inner.operator == "~":
            return eliminate_double_negation(inner.operand1)
        else:
            return StrictWFF(operator=wff.operator, operand1=inner)

    if wff.type == BINARY_WFF:
        left = eliminate_double_negation(wff.operand1)
        right = eliminate_double_negation(wff.operand2)
        return StrictWFF(operator=wff.operator, operand1=left, operand2=right)

    return wff

# Below are 3 functions from an old type just called WFF which functioned slightly differently
def demorgans(wff: StrictWFF) -> StrictWFF:
    """
    Applies De Morgan’s laws and pushes negations down to atomic level.
      ¬(A ∧ B) → (¬A ∨ ¬B)
      ¬(A ∨ B) → (¬A ∧ ¬B)
      ¬¬A → A
    """
    if wff.type == ATOMIC_WFF:
        return wff

    # --- Negation case ---
    if wff.type == UNARY_WFF and wff.operator == "~":
        inner = demorgans(wff.operand1)

        # Double negation
        if inner.type == UNARY_WFF and inner.operator == "~":
            return demorgans(inner.operand1)

        # De Morgan’s transformations
        if inner.type == BINARY_WFF:
            if inner.operator == "∧":
                new_op = "∨"
            elif inner.operator == "∨":
                new_op = "∧"
            else:
                # If it’s not AND or OR, just return the negation as is
                return StrictWFF(operator="~", operand1=inner)

            not_left = StrictWFF(operator="~", operand1=inner.operand1)
            not_right = StrictWFF(operator="~", operand1=inner.operand2)
            return StrictWFF(operator=new_op,
                              operand1=demorgans(not_left),
                              operand2=demorgans(not_right))

        # Atomic negation
        return StrictWFF(operator="~", operand1=inner)

    # --- Binary case ---
    if wff.type == BINARY_WFF:
        left = demorgans(wff.operand1)
        right = demorgans(wff.operand2)
        return StrictWFF(operator=wff.operator, operand1=left, operand2=right)

    return wff

def distribute_or_over_and_helper(left: StrictWFF, right: StrictWFF) -> StrictWFF:
    """
    Apply distributive laws to push OR inside AND:
      (A ∨ (B ∧ C)) → ((A ∨ B) ∧ (A ∨ C))
      ((A ∧ B) ∨ C) → ((A ∨ C) ∧ (B ∨ C))
    """
    if left.type == BINARY_WFF and left.operator == "∧":
        A, B = left.operand1, left.operand2
        return StrictWFF(
            operator="∧",
            operand1=distribute_or_over_and(A, right),
            operand2=distribute_or_over_and(B, right),
        )

    if right.type == BINARY_WFF and right.operator == "∧":
        A, B = right.operand1, right.operand2
        return StrictWFF(
            operator="∧",
            operand1=distribute_or_over_and(left, A),
            operand2=distribute_or_over_and(left, B),
        )

    return StrictWFF(operator="∨", operand1=left, operand2=right)
