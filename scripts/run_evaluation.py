
import json
import time
from pathlib import Path
from statistics import mean

from app.orchestrator import process_question


BASE_DIR = Path(__file__).resolve().parent.parent
TEST_CASES_FILE = BASE_DIR / "evaluation" / "test_cases.json"
RESULTS_FILE = BASE_DIR / "evaluation" / "evaluation_results.json"


def load_test_cases():
    with open(TEST_CASES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_keywords(answer: str, expected_keywords: list[str]) -> bool:
    answer_lower = answer.lower()
    return all(
        keyword.lower() in answer_lower
        for keyword in expected_keywords
    )


def check_status(applicable: bool, passed: bool) -> str:
    if not applicable:
        return "NOT APPLICABLE"
    return "PASS" if passed else "FAIL"


def evaluate_test_case(index: int, test_case: dict) -> dict:
    question = test_case["question"]
    expected_keywords = test_case["expected_keywords"]
    expected_route = test_case["expected_route"]

    start_time = time.perf_counter()
    response = process_question(question=question, top_k=3)
    latency = time.perf_counter() - start_time

    actual_route = response.get("route")
    result = response.get("result") or {}

    if actual_route == "blocked":
        answer = result.get("message", "blocked")
    else:
        answer = result.get("answer") or result.get("message", "")

    sources = result.get("sources", [])
    answer_lower = answer.lower()

    keyword_pass = check_keywords(answer, expected_keywords)
    route_pass = actual_route == expected_route

    not_found = "not found" in answer_lower
    citation_present = "[source" in answer_lower
    source_available = len(sources) > 0

    # Citation and retrieval checks apply to supported RAG answers.
    rag_answer_applicable = (
        actual_route == "rag" and not not_found
    )

    citation_pass = (
        not rag_answer_applicable or citation_present
    )
    retrieval_pass = (
        not rag_answer_applicable or source_available
    )

    # Security check applies to tests intended to be blocked.
    security_applicable = expected_route == "blocked"
    security_pass = (
        not security_applicable or actual_route == "blocked"
    )

    # Unsupported handling applies only to explicitly marked tests.
    unsupported_expected = test_case.get("expect_unsupported", False)
    unsupported_pass = (
        actual_route == "rag"
        and not_found
        and not source_available
    )
    unsupported_applicable = unsupported_expected

    checks = {
        "keyword_check": keyword_pass,
        "route_check": route_pass,
        "citation_check": citation_pass,
        "retrieval_check": retrieval_pass,
        "security_check": security_pass,
        "unsupported_question_check": unsupported_pass,
    }

    applicability = {
        "keyword_check": True,
        "route_check": True,
        "citation_check": rag_answer_applicable,
        "retrieval_check": rag_answer_applicable,
        "security_check": security_applicable,
        "unsupported_question_check": unsupported_applicable,
    }

    check_statuses = {
        name: check_status(applicability[name], checks[name])
        for name in checks
    }

    applicable_checks_passed = all(
        checks[name]
        for name in checks
        if applicability[name]
    )

    return {
        "test_case": index,
        "question": question,
        "expected_route": expected_route,
        "actual_route": actual_route,
        "checks": check_statuses,
        "keyword_check": keyword_pass,
        "route_check": route_pass,
        "citation_check": check_statuses["citation_check"],
        "retrieval_check": check_statuses["retrieval_check"],
        "security_check": check_statuses["security_check"],
        "unsupported_question_check": check_statuses[
            "unsupported_question_check"
        ],
        "citation_present": citation_present,
        "citation_applicable": rag_answer_applicable,
        "source_available": source_available,
        "source_count": len(sources),
        "unsupported_expected": unsupported_expected,
        "unsupported_detected": not_found,
        "passed": applicable_checks_passed,
        "latency_seconds": round(latency, 3),
        "failure_reasons": [
            name
            for name in checks
            if applicability[name] and not checks[name]
        ],
    }


def percentage(numerator: int, denominator: int):
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 2)


def run_evaluation():
    test_cases = load_test_cases()
    results = []

    for index, test_case in enumerate(test_cases, start=1):
        result = evaluate_test_case(index, test_case)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"\n[{status}] Test {index}: {result['question']}")
        print(
            f"  Route: {result['actual_route']} "
            f"(expected: {result['expected_route']})"
        )

        for name, check in result["checks"].items():
            print(f"  {name}: {check}")

        print(f"  Sources: {result['source_count']}")
        print(f"  Latency: {result['latency_seconds']} seconds")

        if result["failure_reasons"]:
            print("  Failed checks: " + ", ".join(
                result["failure_reasons"]
            ))

    total = len(results)
    passed = sum(result["passed"] for result in results)
    failed = total - passed
    latencies = [result["latency_seconds"] for result in results]

    citation_results = [
        result for result in results if result["citation_applicable"]
    ]
    retrieval_results = [
        result for result in results if result["citation_applicable"]
    ]
    unsupported_results = [
        result for result in results if result["unsupported_expected"]
    ]
    security_results = [
        result for result in results
        if result["expected_route"] == "blocked"
    ]

    summary = {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "score_percent": percentage(passed, total),
        "route_accuracy_percent": percentage(
            sum(result["route_check"] for result in results),
            total,
        ),
        "citation_presence_percent": percentage(
            sum(result["citation_present"] for result in citation_results),
            len(citation_results),
        ),
        "source_availability_percent": percentage(
            sum(result["source_available"] for result in retrieval_results),
            len(retrieval_results),
        ),
        "security_pass_percent": percentage(
            sum(result["security_check"] == "PASS"
                for result in security_results),
            len(security_results),
        ),
        "unsupported_handling_pass_percent": percentage(
            sum(result["unsupported_question_check"] == "PASS"
                for result in unsupported_results),
            len(unsupported_results),
        ),
        "average_latency_seconds": round(mean(latencies), 3)
        if latencies else 0,
        "max_latency_seconds": round(max(latencies), 3)
        if latencies else 0,
        "results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Overall pass rate: {summary['score_percent']}%")
    print(f"Route accuracy: {summary['route_accuracy_percent']}%")
    print(f"Citation presence: {summary['citation_presence_percent']}%")
    print(f"Source availability: {summary['source_availability_percent']}%")
    print(f"Security checks passed: {summary['security_pass_percent']}%")
    print(
        "Unsupported handling passed: "
        f"{summary['unsupported_handling_pass_percent']}%"
    )
    print(f"Average latency: {summary['average_latency_seconds']} seconds")
    print(f"Maximum latency: {summary['max_latency_seconds']} seconds")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
