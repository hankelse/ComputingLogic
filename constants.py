LOGICAL_ENTAILMENT_DATA_PATH = "logical-entailment-dataset-master/data/test_easy.txt"
from typing import Literal 


# My Symbols
AND = '∧'
OR = '∨'
IMPLIES = '→'
NOT = '~'
XOR = "⊕"

EXISTENTIAL_Q = "∃"
UNIVERSAL_Q = "∀"


OPERATORS = [AND, OR, IMPLIES, NOT, EXISTENTIAL_Q, UNIVERSAL_Q]

OperatorType = Literal["∧", "∨", "→", "~", "⊕"] 
QuantifierType = Literal['∀', '∃']
UnaryOperator = Literal["~"]
BinaryOperator = Literal["∧", "∨", "→", "⊕"]

UNARY_OPERATORS = {"~"}
BINARY_OPERATORS = {"∧", "∨", "→", "⊕"}


ATOMIC_WFF = "atomic_wff"
UNARY_WFF = "unary_wff"
BINARY_WFF = "binary_wff"
QUANTIFIER_WFF = "quantifier_wff"



# Argument Classifications
VALID = "valid" # conlusion must be true if premises are all true
INVALID = "invalid" # conclusion can be false when the premises are true