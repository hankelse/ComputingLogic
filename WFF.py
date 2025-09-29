from constants import OPERATORS
from constants import NOT, OR, AND, IMPLIES


# def find_main_operator(string):
#     '''
#     Finds the outermost operator: The first operator at depth 0
#         return before_operator, operator, after_operator
#     If none to be found
#         return None    
#     '''
#     # If it contains no operators, return None
#     if not any(op in string for op in OPERATORS):  return None

#     # Find the operator
#     operator = None
#     search_depth = 0 ## Covers if the whole thing is wrapped in parantheses because non at depth 0 will be found but there will be operators
    
#     while operator == None:
#         current_depth = 0
#         for char in string:
#             if char == "(": 
#                 current_depth += 1
#             elif char == ")":
#                 current_depth -= 1
#             elif char in OPERATORS and current_depth == search_depth:
#                 operator = char
#                 break

#         search_depth += 1
#     return operator
    
def find_main_operator(string):
    """
    Finds the outermost operator at depth 0.
    Binary operators (AND, OR, IMPLIES) take precedence over unary (NOT).
    """
    binary_ops = {AND, OR, IMPLIES}
    unary_ops = {NOT}

    current_depth = 0
    found_unary = None

    for i, char in enumerate(string):
        if char == "(":
            current_depth += 1
        elif char == ")":
            current_depth -= 1
        elif current_depth == 0:
            if char in binary_ops:
                return char   # immediately return the binary operator
            elif char in unary_ops and found_unary is None:
                found_unary = char   # save, but keep looking

    return found_unary  # only returned if no binary operator was found





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
    def __init__(self, string, from_WFF = False, main_operator = None, operands = None):
        if from_WFF:
            self.main_operator = main_operator
            self.operands = operands

            #Type
            if self.main_operator == None:
                self.type = ATOMIC_WFF
            elif self.main_operator in UNARY_OPS:
                self.type = UNARY_WFF
            else:
                self.type = BINARY_WFF
            

            # def to_string(wff):
            #     """
            #     Build a string representation of the WFF
            #     based on its operator and operands.
            #     """
            #     if wff.type == ATOMIC_WFF:
            #         return wff.string if wff.string else "?"
                
            #     elif wff.type == UNARY_WFF:
            #         return f"{wff.main_operator}{to_string(wff.operands[0])}"
                
            #     elif wff.type == BINARY_WFF:
            #         left = to_string(wff.operands[0])
            #         right = to_string(wff.operands[1])
            #         return f"({left}{wff.main_operator}{right})"
                
            #     else:
            #         return "<?>"
            
            # self.string = to_string(self)

            

        else:

            #Need to remove wrapping parentheses
            string = strip_outer_parentheses(string.replace(" ", ""))
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
            # print(f"string = ", string)



            #Type
            if self.main_operator == None:
                self.type = ATOMIC_WFF
            elif self.main_operator in UNARY_OPS:
                self.type = UNARY_WFF
                main_op_index = self.string.index(self.main_operator)
                self.operands = [
                    WFF(self.string[main_op_index+1::])]
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
            
                # print(f"For this WFF: {self.string}.   \n\t main_operator = \t {self.main_operator} \n\t operands = \t {self.operands}")
                pass

    def __str__ (self):
        string = ""
        if self.type == ATOMIC_WFF:
            string = self.string
        
        elif self.type == UNARY_WFF:
            string =  f"{self.main_operator}{str(self.operands[0])}"
        
        elif self.type == BINARY_WFF:
            if self.operands[0].type in [ATOMIC_WFF, UNARY_WFF]: 
                left = str(self.operands[0])
            else:
                left = f"({str(self.operands[0])})"
            if self.operands[1].type in [ATOMIC_WFF, UNARY_WFF]: 
                right = str(self.operands[1])
            else:
                right = f"({str(self.operands[1])})"
            # right = str(self.operands[1])

            

            string =  f"{left} {self.main_operator} {right}"
        
        return f"{START_BOLD}{string}{END_BOLD}"
    
        # return str(START_BOLD + self.string + END_BOLD)
    
    def __repr__ (self):
        return (str(self))
        # return str(START_BOLD + self.string + END_BOLD)
    

    # We need a way to find all of the ways a conclusion can be false.
    
    def made_false(self):
        # Returns a list of assignments (dictionaries) that would make this WFF false, with any other non-specified assignments
        if self.type == ATOMIC_WFF:
            return [{self.string : False}]
        
        elif self.main_operator == NOT:
            return self.operands[0].made_true()

        elif self.main_operator == OR:
            # True if either are made true
            op_1_true_assignments = self.operands[0].made_false()
            op_2_true_assignments = self.operands[1].made_false()
            assignments = []
            for asgn_1 in op_1_true_assignments:
                for asgn_2 in op_2_true_assignments:
                    asgn = asgn_1.copy()
                    asgn.update(asgn_2)
                    assignments.append(asgn)
            return assignments
        
        elif self.main_operator == AND:
            # False if either are made false
            op_1_true_assignments = self.operands[0].made_false()
            op_2_true_assignments = self.operands[1].made_false()
            return op_1_true_assignments + op_2_true_assignments # Concat them --> or
        
        elif self.main_operator == IMPLIES:
            # False if first operator is true, and the second is false
            op1_true = self.operands[0].made_true()
            # print("implies false: op1 is true when:", op1_true, self.operands[0].type, strip_outer_parentheses(repr(self.operands[0].string)))
            op2_false = self.operands[1].made_false()

            assignments = []
            for asgn_1 in op1_true:
                for asgn_2 in op2_false:
                    asgn = asgn_1.copy()
                    asgn.update(asgn_2)
                    assignments.append(asgn)

            return assignments

        



    def made_true(self):
        # Returns a list of assignments (dictionaries) that would make this WFF true, with any other non-specified assignments
        if self.type == ATOMIC_WFF:
            return [{self.string : True}]
    
        elif self.main_operator == NOT:
            return self.operands[0].made_false()
        
        elif self.main_operator == OR:
            # True if either are made true
            op_1_true_assignments = self.operands[0].made_true()
            op_2_true_assignments = self.operands[1].made_true()
            return op_1_true_assignments + op_2_true_assignments # Concat them --> or
        
        elif self.main_operator == AND:
                # True if both are made true
                op_1_true_assignments = self.operands[0].made_true()
                op_2_true_assignments = self.operands[1].made_true()
                assignments = []
                for asgn_1 in op_1_true_assignments:
                    for asgn_2 in op_2_true_assignments:
                        asgn = asgn_1.copy()
                        asgn.update(asgn_2)
                        assignments.append(asgn)
                return assignments
        
        elif self.main_operator == IMPLIES:
            # True if first operator is false, or if second is true

            op1_false = self.operands[0].made_false()
            op2_true = self.operands[1].made_true()
            return op1_false + op2_true








# def strip_outer_parentheses(string):
#     if string[0] != "(": return string
#     if string[-1] != ")": return string
    
#     parentheses_counter = 0
#     pc_has_left_zero = False

#     for char in string[1:]:
#         if char == "(": 
#             parentheses_counter += 1
#             pc_has_left_zero = True
#         elif char == ")": 
#             parentheses_counter -= 1
#             pc_has_left_zero = True

#         if pc_has_left_zero and parentheses_counter == 0:
#             return string

    
#     if parentheses_counter == -1:
#         return string[1:-1]

def strip_outer_parentheses(s: str) -> str:
    if not s.startswith("(") or not s.endswith(")"):
        return s
    
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and i != len(s) - 1:
                # Outer parens do not wrap the whole string
                return s
    # If we finished and depth == 0, the outer () do wrap the whole string
    return s[1:-1]

        



