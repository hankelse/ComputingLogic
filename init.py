from itertools import chain
from get_data import get_folio_data, reshape_data, relabel_folio_data
from argument import Argument
from WFFs.WFF_conversion import strict_to_cnf 
from constants import VALID, INVALID

# Toggle verbosity here
VERBOSE_MODE = True


def main():
    # === 1. Load and prepare dataset ===
    f_data = get_folio_data()
    arguments, labels, maps = reshape_data(f_data)
    labels = relabel_folio_data(labels)

    # === 2. Process and evaluate arguments ===
    total, correct = 0, 0

    for i, (premises_raw, conclusion_raw) in enumerate(arguments[:20]):  # limit for sanity
        total += 1
        expected = labels[i] if i < len(labels) else None

        if VERBOSE_MODE:
            print("\n" + "=" * 80)
            print(f"ARGUMENT #{i+1}")
            print("=" * 80)

        # --- Create argument ---
        argument = Argument(premises_raw, conclusion_raw)

        if not argument.solvable(): continue

        if VERBOSE_MODE:
            print("\n--- Original Argument ---")
            print(argument)

        # --- Step 1: Quantifier Expansion ---
        result = argument.expand_quantifiers()


        # --- Step 2: Convert to CNF ---
        cnf_wff = argument.to_cnf()

        if VERBOSE_MODE:
            print("\n--- CNF Form ---")
            print(cnf_wff)
            print("\nCNF Clauses:")
            for clause in cnf_wff.get_clauses():
                print(clause)

        # --- Step 3: Solve with PySAT ---
        is_valid, counterexample = argument.solve()
        computed_label = VALID if is_valid else INVALID
        matches = expected is None or computed_label == expected

        if VERBOSE_MODE:
            print("\n--- SAT Evaluation ---")
            print(f"Expected: {expected}")
            print(f"Computed: {computed_label}")
            if not is_valid and counterexample:
                print("Counterexample model:")
                for var, val in counterexample.items():
                    print(f"  {var} = {val}")
            print(f"✅ Match: {matches}")
            print("=" * 80 + "\n")
        else:
            status_icon = "✅" if matches else "❌"
            print(
                f"{status_icon}  Argument #{i+1:02d}: "
                f"Expected={expected:7s}  |  Solved={computed_label:7s}  "
                f"{'(Counterexample found)' if not is_valid else ''}"
            )

        if matches:
            correct += 1

    # === 3. Summary ===
    print("\n" + "=" * 80)
    print("RESULT SUMMARY")
    print("=" * 80)
    print(f"Total arguments evaluated: {total}")
    print(f"Correctly matched labels:   {correct}")
    print(f"Accuracy:                   {correct / total:.2%}")
    print("=" * 80)


if __name__ == "__main__":
    main()
