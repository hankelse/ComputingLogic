LOGICAL_ENTAILMENT_DATA_PATH = "logical-entailment-dataset-master/data/test_easy.txt"



# My Symbols
AND = 'Λ'
OR = 'V'
IMPLIES = '→'
NOT = '~'

EXISTENTIAL_Q = "∃"
UNIVERSAL_Q = "∀"


OPERATORS = [AND, OR, IMPLIES, NOT, EXISTENTIAL_Q, UNIVERSAL_Q]


# Argument Classifications
VALID = "valid" # conlusion must be true if premises are all true
INVALID = "invalid" # conclusion can be false when the premises are true