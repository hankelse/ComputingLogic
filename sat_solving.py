from get_data import get_folio_data, relabel_folio_data, reshape_data
from testing import run_tests
from pprint import pprint
from constants import VALID, INVALID, NOT, OR, AND, IMPLIES
import itertools
from WFF import WFF
import psa








def main():

    # Get foilio data
    f_data = get_folio_data()

    # Format data
    arguments, labels, maps = reshape_data(f_data)

    # Relabel maps
    labels = relabel_folio_data(labels)

    # Test argument
    premises = [
        "a", str(NOT+"b"), str("a"+OR+"b"), str(NOT+"a"+OR+"c"), str(NOT+"a"+AND+"c"), str(NOT+"a"+IMPLIES+"c"), 
        (f"({NOT}a {OR} b) {IMPLIES} {NOT} (a {AND} {NOT} c)")
    ]
    conclusion = "c"
    argument = (premises, conclusion)

    for p in premises[3:]:
        print(p, "-->", end="")
        p = WFF(p)
        print(p)

        print("True:", p.made_true())
        print("False:", p.made_false())


    pass




main() 