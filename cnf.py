from WFF import WFF, ATOMIC_WFF, UNARY_WFF, BINARY_WFF
from constants import IMPLIES, AND, OR, NOT

'''
Converts WFFS into CNF


    1) Switch Implications (a->b, -a V b)

    2) Move negations inward (also remove double negation)
        If negation is main operator, but operand isn't atomic... deMorgan's Laws

'''

def eliminate_implications(wff : WFF):


    if wff.type == ATOMIC_WFF:
        return wff

    elif wff.type == UNARY_WFF:
        op = eliminate_implications(wff.operands[0])
        wff.operands = [op]
        return wff
    
    elif wff.type == BINARY_WFF:
        op1 = eliminate_implications(wff.operands[0])
        op2 = eliminate_implications(wff.operands[1])

        if wff.main_operator == IMPLIES:
            not_op1 = WFF("", True, NOT, [op1])

            wff.main_operator = OR
            wff.operands = [not_op1, op2]
            return wff
        
        wff.operands = [op1, op2]
        return wff
    else:
        TypeError(f"Don't know what wff type {wff.type} is.")


def eliminate_double_negations(wff : WFF):
    if wff.type == ATOMIC_WFF: return wff

    if wff.type == UNARY_WFF: 
        if wff.main_operator == NOT:
            child = wff.operands[0]
            if child.main_operator == NOT:
                return child.operands[0]
        
            else:
                op = eliminate_double_negations(wff.operands[0])
                wff.operands = [op]
                return wff
    
    if wff.type == BINARY_WFF:
        op1 = eliminate_double_negations(wff.operands[0])
        op2 = eliminate_double_negations(wff.operands[1])
        wff.operands = [op1, op2]
        return wff


def demorgans(wff : WFF):
    if wff.type == ATOMIC_WFF: return wff

    if wff.type == UNARY_WFF: 
        child = demorgans(wff.operands[0])

        if child.type == BINARY_WFF:
            if child.main_operator == AND: new_op = OR
            elif child.main_operator == OR: new_op = AND

            child_op1 = demorgans(child.operands[0])
            child_op2 = demorgans(child.operands[1])
            
            not_child_op1 = WFF("", True, NOT, [child_op1])
            not_child_op2 = WFF("", True, NOT, [child_op2])

            return WFF("", True, new_op, [not_child_op1, not_child_op2])
        else:
            wff.operands = [child]
            return wff

    if wff.type == BINARY_WFF:
        op1 = demorgans(wff.operands[0])
        op2 = demorgans(wff.operands[1])

        wff.operands = [op1, op2]
        return wff



def distribute_or_over_and(left: WFF, right: WFF) -> WFF:
    """
    Apply distributive laws to push OR inside AND:
      (A ∨ (B ∧ C)) -> (A ∨ B) ∧ (A ∨ C)
      ((A ∧ B) ∨ C) -> (A ∨ C) ∧ (B ∨ C)
    """
    if left.main_operator == AND:
        A, B = left.operands
        return WFF(None, from_WFF=True, main_operator=AND, operands=[
            distribute_or_over_and(A, right),
            distribute_or_over_and(B, right)
        ])

    if right.main_operator == AND:
        A, B = right.operands
        return WFF(None, from_WFF=True, main_operator=AND, operands=[
            distribute_or_over_and(left, A),
            distribute_or_over_and(left, B)
        ])

    return WFF(None, from_WFF=True, main_operator=OR, operands=[left, right])


def conjunction_to_disjunction(wff: WFF) -> WFF:
    """
    Convert a WFF into CNF by distributing OR over AND recursively.
    """
    if wff.type == ATOMIC_WFF:
        return wff

    if wff.type == UNARY_WFF:
        return WFF(None, from_WFF=True, main_operator=wff.main_operator,
                   operands=[conjunction_to_disjunction(wff.operands[0])])

    if wff.type == BINARY_WFF:
        left = conjunction_to_disjunction(wff.operands[0])
        right = conjunction_to_disjunction(wff.operands[1])

        if wff.main_operator == OR:
            return distribute_or_over_and(left, right)
        else:  # AND
            return WFF(None, from_WFF=True, main_operator=AND, operands=[left, right])

    return wff


def to_cnf(wff: WFF) -> WFF:
    """
    Full CNF pipeline:
      1. Eliminate implications
      2. Push negations inward (DeMorgan’s, double neg)
      3. Distribute OR over AND
    """
    wff = eliminate_implications(wff)
    wff = demorgans(wff)
    wff = eliminate_double_negations(wff)
    wff = conjunction_to_disjunction(wff)
    return wff

tests = [
    f"a {IMPLIES} b",
    f"{NOT} a {IMPLIES} b",
    f"(a {OR} b) {IMPLIES} (b {IMPLIES} c)",
    f"{NOT}({NOT}a)",
    f"{NOT} a {IMPLIES} b",
    f"{NOT}(a {IMPLIES} b)",
    f"a {AND} b",
    f"a {OR} (c {AND} b)",
    f"(a {AND} b) {OR} (c {OR} d)",  # distributivity both sides
    f"(a {OR} b) {AND} (c {OR} d)",  # already CNF
    f"(a {IMPLIES} b) {AND} ({NOT}c {OR} (d {AND} e))",  # mix of all
    f"{NOT}((a {AND} b) {IMPLIES} (c {OR} d))",          # negated implication
    f"(a {IMPLIES} (b {OR} c)) {AND} ({NOT}d {IMPLIES} (e {AND} f))"  # real stress test
]

wff_tests = [WFF(test) for test in tests]

for wt in wff_tests:
    print(f"Given: {wt}")

    wt = eliminate_implications(wt)
    print(f"\tNo Implies: \t{wt}")

    wt = eliminate_double_negations(wt)
    print(f"\tNo ~~:      \t{wt}")

    wt = demorgans(wt)
    print(f"\tDeMorgan's: \t{wt}")
    
    wt = eliminate_double_negations(wt)
    print(f"\tNo ~~:      \t{wt}")

    wt = conjunction_to_disjunction(wt)
    print(f"\tNo ANDS:    \t{wt}")
