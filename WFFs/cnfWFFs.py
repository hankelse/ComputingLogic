'''
CNF wffs are a more relaxed version of WFFs where 
- the only binary operators are disjunction and conjunction
- the only unary operators are negation
- there are no quantifiers

A disjunctive wff may have 2 or more operands
A conjunctive wff may have 2 or more operands

'''

# cnfWFFs.py
from __future__ import annotations
from typing import Optional, List, Literal
from copy import deepcopy

from constants import AND, OR, NOT

from constants import AND, OR, NOT, ATOMIC_WFF, UNARY_WFF


CONJUNCTIVE_WFF = "conjunctive_wff"
DISJUNCTIVE_WFF = "disjunctive_wff"


class CnfWFF:
    """
    A specialized WFF type that represents formulas already in CNF form.

    Structure (max depth = 4):
        conjunctive_wff: conjunction (∧) of disjunctive_wffs
        disjunctive_wff: disjunction (∨) of literals (atomic or negated)
        unary_wff: negated atomic (~P)
        atomic_wff: atomic literal (P)

    This ensures that all CNF formulas are represented as:
        (clause_1 ∧ clause_2 ∧ ...)   where each clause_i = (lit_1 ∨ lit_2 ∨ ...)
        and each lit_j is atomic or unary (~atomic).
    """

    def __init__(
        self,
        atom: Optional[str] = None,
        operator: Optional[str] = None,
        operands: Optional[List[CnfWFF]] = None,
    ):
        self.atom = atom
        self.operator = operator
        self.operands: List[CnfWFF] = operands or []
        self.type = self.assign_and_enforce_type()
        self._enforce_cnf_depth_constraints()

    # ==========================================================
    # --- Type assignment and enforcement ---
    # ==========================================================

    def assign_and_enforce_type(self) -> str:
        """Infers and enforces the CNF type and ensures flattening."""
        if self.atom:
            assert self.operator is None and not self.operands
            return ATOMIC_WFF

        if self.operator == NOT:
            assert len(self.operands) == 1, "Negation must have exactly one operand."
            inner = self.operands[0]
            assert inner.type == ATOMIC_WFF, f"Invalid CNF negation: {repr(inner)} is not atomic."
            return UNARY_WFF

        if self.operator == OR:
            assert len(self.operands) >= 2, "∨ must have at least two operands."
            for op in self.operands:
                assert op.type in (ATOMIC_WFF, UNARY_WFF, DISJUNCTIVE_WFF), (
                    f"Invalid disjunction operand: {repr(op)}"
                )

            # Flatten nested disjunctions
            flattened = []
            for op in self.operands:
                if op.type == DISJUNCTIVE_WFF and op.operator == OR:
                    flattened.extend(op.operands)
                else:
                    flattened.append(op)
            self.operands = flattened
            return DISJUNCTIVE_WFF

        if self.operator == AND:
            assert len(self.operands) >= 2, "∧ must have at least two operands."
            for op in self.operands:
                assert op.type in (DISJUNCTIVE_WFF, ATOMIC_WFF, UNARY_WFF, CONJUNCTIVE_WFF), (
                    f"Invalid conjunction operand: {repr(op)}"
                )

            # Flatten nested conjunctions
            flattened = []
            for op in self.operands:
                if op.type == CONJUNCTIVE_WFF and op.operator == AND:
                    flattened.extend(op.operands)
                else:
                    flattened.append(op)
            self.operands = flattened
            return CONJUNCTIVE_WFF

        raise ValueError(f"Invalid CNF structure: {self}")

    def _enforce_cnf_depth_constraints(self):
        """
        Ensures that CNF structural depth <= 4 and each layer obeys CNF hierarchy:
            conjunctive_wff -> disjunctive_wffs
            disjunctive_wff -> unary or atomic
            unary_wff -> atomic
        """
        def depth(node: CnfWFF) -> int:
            if not node.operands:
                return 1
            return 1 + max(depth(op) for op in node.operands)

        d = depth(self)
        assert d <= 4, f"CNF depth {d} exceeds allowed limit (max 4)."

        # Conjunctive layer check
        if self.type == CONJUNCTIVE_WFF:
            for clause in self.operands:
                assert clause.type in (DISJUNCTIVE_WFF, ATOMIC_WFF, UNARY_WFF), (
                    f"Conjunction contains invalid element: {repr(clause)}"
                )

        # Disjunctive layer check
        if self.type == DISJUNCTIVE_WFF:
            for lit in self.operands:
                assert lit.type in (ATOMIC_WFF, UNARY_WFF), (
                    f"Disjunction contains invalid element: {repr(lit)}"
                )

        # Unary layer check
        if self.type == UNARY_WFF:
            assert self.operands[0].type == ATOMIC_WFF, "Negation must apply only to atomic literal."

    def __repr__(self) -> str:
        if self.type == ATOMIC_WFF:
            return self.atom
        elif self.type == UNARY_WFF:
            return f"{NOT}{repr(self.operands[0])}"
        elif self.type == DISJUNCTIVE_WFF:
            return "(" + " ∨ ".join(repr(op) for op in self.operands) + ")"
        elif self.type == CONJUNCTIVE_WFF:
            return "(" + " ∧ ".join(repr(op) for op in self.operands) + ")"
        else:
            TypeError (f"CNF WFF has type {self.type}")

    # ==========================================================
    # --- CNF Utilities ---
    # ==========================================================


    def negate(self) -> "CnfWFF":
        """
        Return ¬self as a valid CnfWFF.
        We convert to StrictWFF, negate, fully normalize to CNF, then convert back.
        """
        from WFFs.strictWFFs import StrictWFF
        from WFFs.WFF_conversion import strict_to_cnf

        strict = self.to_strict()
        neg_strict = StrictWFF(operator=NOT, operand1=strict)
        return strict_to_cnf(neg_strict)






    def flatten_conjunctions(self) -> List[CnfWFF]:
        """Return a flat list of disjunctive clauses."""
        if self.type == CONJUNCTIVE_WFF:
            clauses = []
            for op in self.operands:
                clauses.extend(op.flatten_conjunctions())
            return clauses
        else:
            return [self]

    def flatten_disjunctions(self) -> List[CnfWFF]:
        """Return a flat list of literals within this clause."""
        if self.type == DISJUNCTIVE_WFF:
            lits = []
            for op in self.operands:
                lits.extend(op.flatten_disjunctions())
            return lits
        else:
            return [self]

    def get_literals(self) -> List[str]:
        """Return all literal strings in this CNF (atoms and negated atoms)."""
        if self.type == ATOMIC_WFF:
            return [self.atom]
        if self.type == UNARY_WFF:
            return [f"{NOT}{self.operands[0].atom}"]
        if self.type == DISJUNCTIVE_WFF:
            lits = []
            for op in self.operands:
                lits.extend(op.get_literals())
            return lits
        if self.type == CONJUNCTIVE_WFF:
            lits = []
            for c in self.operands:
                lits.extend(c.get_literals())
            return lits
        return []

    def get_clauses(self) -> List[List[str]]:
        """Return CNF as list of clauses, each a list of literals."""
        if self.type == CONJUNCTIVE_WFF:
            return [clause.get_literals() for clause in self.operands]
        elif self.type == DISJUNCTIVE_WFF:
            return [self.get_literals()]
        elif self.type in (ATOMIC_WFF, UNARY_WFF):
            return [[lit for lit in self.get_literals()]]
        else:
            raise ValueError("Invalid CNF WFF structure.")

    def to_strict(self):
        """
        Convert this CNF WFF into a StrictWFF-equivalent structure for transformation.
        Useful for applying negation or implication elimination.
        """
        from WFFs.strictWFFs import StrictWFF

        if self.type == ATOMIC_WFF:
            return StrictWFF(atom=self.atom)
        if self.type == UNARY_WFF:
            return StrictWFF(operator=NOT, operand1=self.operands[0].to_strict())
        if self.type == DISJUNCTIVE_WFF:
            assert len(self.operands) >= 2
            left = self.operands[0].to_strict()
            right = CnfWFF(operator=self.operator, operands=self.operands[1:]).to_strict() \
                if len(self.operands) > 2 else self.operands[1].to_strict()
            return StrictWFF(operator=self.operator, operand1=left, operand2=right)
        if self.type == CONJUNCTIVE_WFF:
            assert len(self.operands) >= 2
            left = self.operands[0].to_strict()
            right = CnfWFF(operator=self.operator, operands=self.operands[1:]).to_strict() \
                if len(self.operands) > 2 else self.operands[1].to_strict()
            return StrictWFF(operator=self.operator, operand1=left, operand2=right)
        raise ValueError(f"Unsupported CNF WFF type in to_strict: {self.type}")
    
def normalize_cnf(cnf: "CnfWFF") -> "CnfWFF":
    """
    Ensures that CNF structure obeys AND-of-ORs hierarchy
    by distributing OR over AND if needed.
    """
    # Flatten conjunctions/disjunctions recursively
    if cnf.operator == OR:
        # distribute OR over AND
        new_operands = []
        for op in cnf.operands:
            if op.operator == AND:
                # (A ∨ (B ∧ C)) → ((A ∨ B) ∧ (A ∨ C))
                distributed = [
                    normalize_cnf(CnfWFF(operator=OR, operands=[cnf.operands[0], sub]))
                    for sub in op.operands
                ]
                return CnfWFF(operator=AND, operands=distributed)
            new_operands.append(op)
        cnf.operands = new_operands

    elif cnf.operator == AND:
        cnf.operands = [normalize_cnf(op) for op in cnf.operands]

    return cnf