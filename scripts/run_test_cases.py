from pathlib import Path
import json
import sys


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVALUATION_DIR = PROJECT_ROOT / "data" / "test_cases"


# ============================================================
# EVALUATION DATASETS
# ============================================================

EVALUATION_FILES = {
    "PII Detection": "pii_test_cases.json",
    "Fraud Detection": "fraud_test_cases.json",
    "Adjudication": "adjudication_test_cases.json",
    "RAG Accuracy": "rag_test_cases.json",
}


# ============================================================
# HELPERS
# ============================================================

def load_test_cases(file_path: Path):
    """Load evaluation test cases from a JSON file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Evaluation file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Support common JSON structures such as:
        # {"test_cases": [...]}
        # {"cases": [...]}
        if "test_cases" in data:
            return data["test_cases"]

        if "cases" in data:
            return data["cases"]

        # If the dictionary itself represents one test case
        return [data]

    raise ValueError(
        f"Unsupported JSON structure in {file_path}"
    )


def validate_test_case(case, index):
    """Basic validation of an evaluation test case."""

    if not isinstance(case, dict):
        return False, "Test case must be a JSON object"

    if not case:
        return False, "Test case is empty"

    return True, "Valid"


# ============================================================
# DATASET CHECK
# ============================================================

def evaluate_dataset(name: str, filename: str):
    """Validate one evaluation dataset."""

    file_path = EVALUATION_DIR / filename

    try:
        test_cases = load_test_cases(file_path)

    except Exception as exc:
        print(f"\n{name}")
        print("-" * 50)
        print(f"FAILED: {exc}")

        return {
            "name": name,
            "total": 0,
            "passed": 0,
            "failed": 1,
            "status": "FAILED",
        }

    passed = 0
    failed = 0

    for index, case in enumerate(test_cases, start=1):
        valid, message = validate_test_case(case, index)

        if valid:
            passed += 1
        else:
            failed += 1
            print(
                f"  Test case {index}: FAILED - {message}"
            )

    total = len(test_cases)

    status = "PASSED" if failed == 0 else "FAILED"

    print(f"\n{name}")
    print("-" * 50)
    print(f"Test cases : {total}")
    print(f"Passed     : {passed}")
    print(f"Failed     : {failed}")

    if total > 0:
        accuracy = (passed / total) * 100
        print(f"Validation: {accuracy:.1f}%")

    print(f"Status     : {status}")

    return {
        "name": name,
        "total": total,
        "passed": passed,
        "failed": failed,
        "status": status,
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

def run_evaluation():
    print("=" * 70)
    print("AUTONOMOUS CLAIM ADJUDICATION - EVALUATION")
    print("=" * 70)

    if not EVALUATION_DIR.exists():
        print(
            f"\nERROR: Evaluation directory not found:\n"
            f"{EVALUATION_DIR}"
        )
        return 1

    results = []

    for name, filename in EVALUATION_FILES.items():
        result = evaluate_dataset(name, filename)
        results.append(result)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_cases = sum(result["total"] for result in results)
    total_passed = sum(result["passed"] for result in results)
    total_failed = sum(result["failed"] for result in results)

    print("\n")
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    for result in results:
        print(
            f"{result['name']:<25} "
            f"{result['passed']:>3}/{result['total']:<3} "
            f"{result['status']}"
        )

    print("-" * 70)

    if total_cases > 0:
        overall_accuracy = (
            total_passed / total_cases
        ) * 100
    else:
        overall_accuracy = 0.0

    print(f"Total test cases : {total_cases}")
    print(f"Total passed     : {total_passed}")
    print(f"Total failed     : {total_failed}")
    print(f"Overall result   : {overall_accuracy:.1f}%")

    print("=" * 70)

    return 0 if total_failed == 0 else 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(run_evaluation())