from constants import VALID, INVALID

def run_tests(validity_func, arguments, labels):

    
    """
    Runs a validity checker function against test cases.

    Parameters:
    - check_validity: function(premises, conclusion) -> str ("Valid"/"Invalid")
    - arguments: list of tuples ([premises], conclusion)
    - labels: list of expected outputs ("Valid"/"Invalid")

    Returns:
    - None (prints test results)
    """
    total = len(arguments)
    passed = 0

    for i, ((premises, conclusion), expected) in enumerate(zip(arguments, labels), 1):
        try:
            result = validity_func(premises, conclusion)

        ## Check for errors
        except Exception as e:
            print(f"[{i}] ❌ ERROR while running test case:")
            print(f"    Premises:   {premises}")
            print(f"    Conclusion: {conclusion}")
            print(f"    Expected:   {expected}")
            print(f"    Error:      {e}")
            continue

        ## If test passed
        if result == expected:
            passed += 1
            print(f"[{i}] ✅ PASS! Correctly found {result} validity.")
        else:
            print(f"[{i}] ❌ FAIL")
            print(f"    Premises:   {premises}")
            print(f"    Conclusion: {conclusion}")
            print(f"    Expected:   {expected}")
            print(f"    Got:        {result}")

    print("\nSummary:")
    print(f"  Passed {passed}/{total} tests")
    print(f"  Failed {total - passed}/{total} tests")


# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    # Example dataset
    arguments = [
        (["∀x (P(x) → Q(x))", "P(a)"], "Q(a)"),
        (["P(a)"], "Q(a)")
    ]
    labels = ["Valid", "Invalid"]

    # Example checker function (replace with your real one)
    def example_checker(premises, conclusion):
        # return "Valid" if premises == ["∀x (P(x) → Q(x))", "P(a)"] and conclusion == "Q(a)" else "Invalid"
        return "Valid"

    # Run tests
    run_tests(example_checker, arguments, labels)