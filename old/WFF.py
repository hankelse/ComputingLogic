from constants import OPERATORS
from constants import NOT, OR, AND, IMPLIES, UNIVERSAL_Q, EXISTENTIAL_Q
from copy import deepcopy

'''


Strict WFFS --> Quantifers, implications, etc

preprocessing

Only ANd, OR, Negation, no quantifiers, and and or take unlimited operands




UNIT TESTS BEFORE CLEANING
'''



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

            self.quantifier = None

        else:

            self.quantifier = None

            #Need to remove wrapping parentheses
            string = strip_outer_parentheses(string.replace(" ", ""))
            self.string = string

            self.detect_quantifier()

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

            self.domain = None

    def detect_quantifier(self):
        """
        Detect if the WFF string begins with a quantifier (UNIVERSAL_Q or EXISTENTIAL_Q).
        If found, store {'symbol': <quantifier>, 'variable': <var>} in self.quantifier
        and remove it from self.string for further parsing.
        """
        # if len(self.string) < 2:
        #     return  # too short to contain quantifier + variable

        first_char = self.string[0]
        if first_char in [UNIVERSAL_Q, EXISTENTIAL_Q]:
            # assume next char is the variable (like ∀xP(x))
            variable = self.string[1]

            # basic sanity check (variables should be alphabetic)
            if variable.isalpha():
                self.quantifier = {"symbol": first_char, "variable": variable}
                
                # remove the quantifier and variable from the string
                self.string = self.string[2:]

                # optionally remove wrapping parentheses if they exist
                self.string = strip_outer_parentheses(self.string)


    def get_domain(self):
        ''' Returns a list of all atoms in all sub-wffs'''
        if self.domain: return self.domain


        if self.type == ATOMIC_WFF:
            string = repr(self)
            domain = only_lowercase(string)
        elif self.type == UNARY_WFF:
            domain =  self.operands[0].get_domain()
        else:
            domain = self.operands[0].get_domain() + self.operands[1].get_domain()

        return list(set(domain))
    

    # def set_domain(self):
    #     domain = self.get_domain()

    #     if self.type != ATOMIC_WFF:
    #         for operand in self.operands:
    #             operand.set_domain_helper(domain)


    # def set_domain_helper(self, domain):
    #     self.domain = domain
    #     if self.type != ATOMIC_WFF:
    #         for operand in self.operands:
    #             operand.set_domain_helper(domain)
            





    def replace(self, to_replace, replacer):
        if self.type == ATOMIC_WFF:
            if to_replace in self.string:
                self.string = self.string.replace(to_replace, replacer)
        elif self.type == UNARY_WFF:
            self.operands[0].replace(to_replace, replacer)
        else:
            self.operands[0].replace(to_replace, replacer)
            self.operands[1].replace(to_replace, replacer)


    def __str__ (self):        
        return f"{START_BOLD}{repr(self)}{END_BOLD}"
    
        # return str(START_BOLD + self.string + END_BOLD)
    
    def __repr__ (self):
        string = ""
        if self.type == ATOMIC_WFF:
            string = self.string
        
        elif self.type == UNARY_WFF:
            string =  f"{self.main_operator}({repr(self.operands[0])})"
        
        elif self.type == BINARY_WFF:
            if self.operands[0].type in [ATOMIC_WFF, UNARY_WFF]: 
                left = repr(self.operands[0])
            else:
                left = f"({repr(self.operands[0])})"
            if self.operands[1].type in [ATOMIC_WFF, UNARY_WFF]: 
                right = repr(self.operands[1])
            else:
                right = f"({repr(self.operands[1])})"
            string =  f"{left} {self.main_operator} {right}"
        # type(init_string)

        self.string = string
        if self.quantifier:
            string = f"{self.quantifier["symbol"]}{self.quantifier["variable"]} [{string}]"
        else:
            self.string = string
        return string
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
        

    
    def expand_quantifers(self, domain):

        if not self.type == ATOMIC_WFF:
            for op in self.operands:
                op.expand_quantifers(domain)

        if self.quantifier:
            # print(self.quantifier)
            # domain = self.get_domain()

            variable = self.quantifier["variable"]
            quantifier = self.quantifier["symbol"]

            if quantifier == UNIVERSAL_Q: joining_operator = AND
            elif quantifier == EXISTENTIAL_Q: joining_operator = OR
            else: raise NameError

            # print(f"joining op {joining_operator}")

            if variable in domain:
                domain.remove(variable)

            # print(f"domain: {domain}")

            # Create the new wffs
            new_wffs = []
            # print(f"domain= {domain}")
            for atom in domain:
                # print(f"\t for {atom} in {domain}")
                wff_copy = deepcopy(self)
                # print(wff_copy, end = "->")
                wff_copy.replace(variable, atom)
                wff_copy.quantifier = None
                # print(wff_copy)
                new_wffs.append(wff_copy)
            # print(f"newwffs: {new_wffs}")


            # Join all the wffs into a larger one
            # print(len(domain))
            joined = list_to_WFF(new_wffs, joining_operator)
            # print(f"joined {joined}")

            if joined.type != ATOMIC_WFF:
                self.operands = joined.operands
            else:
                self.string = joined.string

            self.main_operator = joined.main_operator
            self.quantifier = None
            self.type = joined.type
        
        







def strip_outer_parentheses(s: str) -> str:
    if (not s.startswith("(") or not s.endswith(")")) and (not s.startswith("[") or not s.endswith("]")):
        return s
    
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(" or "[":
            depth += 1
        elif ch == ")" or "]":
            depth -= 1
            if depth == 0 and i != len(s) - 1:
                # Outer parens do not wrap the whole string
                return s
    # If we finished and depth == 0, the outer () do wrap the whole string
    return s[1:-1]

        





def new_WFF(operator, operand1=None, operand2=None):
    # print(f"new wff! {operator} {operand1} {operand2}")
    ''' For creating a WFF from WFFs'''

    if operand2:
        wff = WFF(f"a {operator} b")
        wff.operands = [operand1, operand2]
        wff.type = BINARY_WFF
    else:
        wff = WFF(f"{operator} b")
        wff.operands = [operand1]
        wff.type = UNARY_WFF

    return wff


def list_to_WFF(list, operator):
    '''
    Takes a list of WFFS and returns them all joined by the operator
    '''
    # if len(list) == 0: return None
    if len(list) == 1: return list[0]

    head = list[0]
    rest = list[1:]

    return list_to_WFF_helper(head, rest, operator)



def list_to_WFF_helper(head, rest, operator):
    # print(f"head {head}, rest {rest}, operator {operator}")

    if len(rest) > 1:
        operand2 = list_to_WFF_helper(rest[0], rest[1:], operator)
    else:
        operand2 = rest[0]



    result = new_WFF(operator, head, operand2)
    
    return result


def only_lowercase(str):
    result = ""
    for char in str:
        if char.islower():
            result += char
    return result
