from constants import OPERATORS


def find_main_operator(string):
    '''
    Finds the outermost operator: The first operator at depth 0
        return before_operator, operator, after_operator
    If none to be found
        return None    
    '''
    # If it contains no operators, return None
    if not any(op in string for op in OPERATORS):  return None

    # Find the operator
    operator = None
    search_depth = 0 ## Covers if the whole thing is wrapped in parantheses because non at depth 0 will be found but there will be operators
    
    while operator == None:
        current_depth = 0
        for char in string:
            if char == "(": 
                current_depth += 1
            elif char == ")":
                current_depth -= 1
            elif char in OPERATORS and current_depth == search_depth:
                operator = char
                break

        search_depth += 1
    return operator
    





"""
Three types of WFFs:
1. Atomic WFFs: 
    Main Operator: None
    Operands: None
2. Unary WFFs:
    Main Operator: ~
    Operands: 1
3. Binary WFFs:
    Main Operator: Λ, V, →, ~, ∃, ∀
    Operands: 2
"""


QUANTIFIERS = set(["∃", "∀"])

UNARY_OPS = set(["~"])
BINARY_OPS = set(["Λ", "V", "→", "~"])

#Types
ATOMIC_WFF = "atomic_wff"
UNARY_WFF = "unary_wff"
BINARY_WFF = "binary_wff"


START_BOLD = "\033[1m"
END_BOLD = "\033[0m"




class WFF:
    def __init__(self, string):
        
        

        #Need to remove wrapping parentheses
        string = strip_outer_parentheses(string)
        self.string = string

        # Main operator
        '''
        WFF's have a main operation:
            - Unary: ~, Ax, Ex
            - Binary: and, or, implies
        Or don't:
            - If they are just an atom or variable: x, a, 
        '''
        self.main_operator = find_main_operator(self.string)


        #Type
        if self.main_operator == None:
            self.type = ATOMIC_WFF
        elif self.main_operator in UNARY_OPS:
            self.type = UNARY_WFF
        else:
            self.type = BINARY_WFF


        # Operands

        # If binary WFF, then operands are on either side
        if self.type == BINARY_WFF:
            main_op_index = self.string.index(self.main_operator)
            self.operands = [
                WFF(self.string[0:main_op_index]), 
                WFF(self.string[main_op_index+1::])
            ]
        
            print(f"For this WFF: {self.string}.   \n\t main_operator = \t {self.main_operator} \n\t operands = \t {self.operands}")
            pass

    def __str__ (self):
        return self.string
    
    def __repr__ (self):
        return str(START_BOLD + self.string + END_BOLD)



def strip_outer_parentheses(string):
    if string[0] != "(": return string
    if string[-1] != ")": return string


    
    parentheses_counter = 0
    pc_has_left_zero = False

    for char in string[1:]:
        if char == "(": 
            parentheses_counter += 1
            pc_has_left_zero = True
        elif char == ")": 
            parentheses_counter -= 1
            pc_has_left_zero = True

        if pc_has_left_zero and parentheses_counter == 0:
            return string

    
    if parentheses_counter == -1:
        return string[1:-1]

        



ab = "aΛ(bΛc)"
a = WFF(ab)

wffs = ["(ab)", "(a)(b)", "(ab(ab))"]
for w in wffs:
    print(f"from: {w} \n to: {strip_outer_parentheses(w)}")



