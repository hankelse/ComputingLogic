
from constants import *
import ast


SYMBOL_SET = {
    "AND" : AND,
    "OR" : OR,
    "NOT" : NOT,
    "IMPLIES" : IMPLIES
}



def load_data(file_path):
    data_dict = {}
    with open(file_path, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")  # read header
        for line in f:
            parts = line.strip().split("\t")

            # unpack the line into variables
            story_id, example_id, conclusion, premises, premises_fol, label, source = parts

            # turn the string lists into actual lists
            premises = ast.literal_eval(premises)
            premises_fol = ast.literal_eval(premises_fol)

            # make a key from story_id + example_id
            key = f"{story_id}_{example_id}"

            # make a dictionary for the rest
            value = {
                "conclusion": conclusion,
                "premises": premises,
                "premises-FOL": premises_fol,
                "label": label == "True",   # convert to boolean
                "source": source
            }

            data_dict[key] = value

    return data_dict




def swap_symbols(string, original_symbols, new_symbols):
    result = ""

    # Invert dict so the symbols point to the name of the operation 
    inverted_original_symbols = {value : key for key, value in original_symbols.items()}


    for char in string:

        if char in inverted_original_symbols.keys():
            operator = inverted_original_symbols[char]
            swapped_symbol = new_symbols[operator]
        
            result += swapped_symbol
        
        else:
            result += char
    
    return result



def get_logical_entailment_data():
    path = LOGICAL_ENTAILMENT_DATA_PATH

    # Their symbols
    le_and = "&"
    le_or = "|"
    le_implies = ">"
    le_not = "~"

    le_symbol_set = {
    "AND" : le_and,
    "OR" : le_or,
    "NOT" : le_not,
    "IMPLIES" : le_implies
    }


    with open(path) as file:
        arguments = file.readlines()

    # print(arguments[0])
    return arguments

# Their symbols
le_and = "&"
le_or = "|"
le_implies = ">"
le_not = "~"

le_symbol_set = {
    "AND" : le_and,
    "OR" : le_or,
    "NOT" : le_not,
    "IMPLIES" : le_implies
    }

# arguments = get_logical_entailment_data()
# first = arguments[0]


# print(first)
# print(swap_symbols(first, le_symbol_set, SYMBOL_SET))
import ast

# ===== FOLIO ===== #

FOLIO_FILE_PATH = "FOLIO-main/data/v0.0/folio-validation.txt"  # constant file path


def load_folio_data():
    data_dict = {}
    with open(FOLIO_FILE_PATH, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")  # read header
        for line_num, line in enumerate(f, start=1):  # start=1 so first data line is key=1
            parts = line.strip().split("\t")

            # unpack the line into variables
            premises, premises_fol, conclusion, conclusion_fol, label = parts

            # parse the lists
            premises = ast.literal_eval(premises)
            premises_fol = ast.literal_eval(premises_fol)

            # use line number as key
            key = line_num

            # build dictionary entry
            value = {
                "premises": premises,
                "premises-FOL": premises_fol,
                "conclusion": conclusion,
                "conclusion-FOL": conclusion_fol,
                "label": label
            }

            data_dict[key] = value

    return data_dict


def reshape_data(dataset):
    X = [(d["premises"], d["conclusion"]) for d in dataset]
    y = [d["label"] for d in dataset]
    maps = [d["map"] for d in dataset]
    return X, y, maps




'''
API function called to get the data in a good, clean format.
'''
def get_folio_data():
    """
    API function called to get the data in a good, clean format.
    Returns: list of dicts:
      {
        "premises": [<compressed FOL premise>, ...],
        "conclusion": <compressed FOL conclusion or "">,
        "label": <label as in source>,
        "map": {<abbreviation>: <original symbol>}
      }
    """
    result = []

    # Get the data into a dictionary (assumes this is defined elsewhere)
    data_dict = load_folio_data()

    for _, value in data_dict.items():
        fol_premises = value.get("premises-FOL", []) or []
        fol_conclusion = value.get("conclusion-FOL", "") or ""
        label = value.get("label")

        # fresh mapping per example
        abbr_map = None
        compressed_premises = []
        for prem in fol_premises:
            comp, abbr_map = compress_fol(prem, abbr_map)
            compressed_premises.append(comp)

        compressed_conclusion = ""
        if fol_conclusion:
            compressed_conclusion, abbr_map = compress_fol(fol_conclusion, abbr_map)

        result.append({
            "premises": compressed_premises,
            "conclusion": compressed_conclusion,
            "label": label,
            "map": abbr_map or {}
        })

    return result


import re
import string

def compress_fol(expression, existing_map=None):
    # Fresh pools for each call
    pred_pool = iter(string.ascii_uppercase)  # A, B, C...
    term_pool = iter(string.ascii_lowercase)  # a, b, c...

    # Split existing map into predicate + term mappings
    pred_map, term_map = {}, {}
    if existing_map:
        for k, v in existing_map.items():
            if k[0].isupper():   # predicates
                pred_map[v] = k
            else:                # terms
                term_map[v] = k

    # Functions to get or assign new symbols
    def get_pred(sym):
        if sym not in pred_map:
            nxt = next(pred_pool)
            # Skip symbols already used
            while nxt in pred_map.values():
                nxt = next(pred_pool)
            pred_map[sym] = nxt
        return pred_map[sym]

    def get_term(sym):
        if sym not in term_map:
            nxt = next(term_pool)
            while nxt in term_map.values():
                nxt = next(term_pool)
            term_map[sym] = nxt
        return term_map[sym]

    # Regex to find predicates with arguments
    pattern = re.compile(r'(\w+)\(([^()]*)\)')

    def replacer(match):
        pred = match.group(1)
        args = [arg.strip() for arg in match.group(2).split(",")]
        return get_pred(pred) + "".join(get_term(a) for a in args)

    compressed_expr = pattern.sub(replacer, expression)

    # Build combined map (inverse of pred_map/term_map)
    full_map = {v: k for k, v in pred_map.items()}
    full_map.update({v: k for k, v in term_map.items()})

    return compressed_expr, full_map


def relabel_folio_data(labels):
    new_labels = []
    for label in labels:
        if label == "True":
            new_labels.append(VALID)
        else:
            new_labels.append(INVALID)
    return new_labels


# Example usage
if __name__ == "__main__":
    dataset = load_folio_data()
    # print(dataset)   # print first example

    # for key, value in dataset.items():
    #     print(f"{key}   Premise 1: {value["premises-FOL"][0]}   Conclusion: {value["conclusion-FOL"]}")

    #     value["premises-FOL"][0]


    p1_worded = dataset[204]["premises-FOL"][0]

    p1, p_map = compress_fol(p1_worded)
    print(p1)
    print(p_map)

    p2_worded = dataset[204]["premises-FOL"][1]

    p2, p_map = compress_fol(p2_worded, p_map)
    print(p2)
    print(p_map)




    