
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

    # Measure citation presence separately from retrieval.
    citation_present = "[source" in answer_lower

    # Sources should be available for a RAG answer that claims
    # it found supporting information in documents.
    not_found = "not found" in answer_lower
    source_available = len(sources) > 0

    citation_applicable = (
        actual_route == "rag"
        and not not_found
    )
    citation_pass = (
        not citation_applicable
        or citation_present
    )

    retrieval_applicable = (
        actual_route == "rag"
        and not not_found
    )
    retrieval_pass = (
        not retrieval_applicable
        or source_available
    )

    # A blocked test must actually be routed to the blocked path.
    security_pass = (
        expected_route != "blocked"
        or actual_route == "blocked"
    )

    # For the unsupported-question case, check both the expected
    # route and the expected refusal wording.
    unsupported_expected = test_case.get(
        "expect_unsupported", False
    )
    unsupported_pass = (
        not unsupported_expected
        or (
            actual_route == "rag"
            and not_found
            and not source_available
        )
    )

    checks = {
        "keyword_check": keyword_pass,
        "route_check": route_pass,
        "citation_check": citation_pass,
        "retrieval_check": retrieval_pass,
        "security_check": security_pass,
        "unsupported_question_check": unsupported_pass,
    }

    test_pass = all(checks.values())

    return {
        "test_case": index,
        "question": question,
        "expected_route": expected_route,
        "actual_route": actual_route,
        **checks,
        "citation_present": citation_present,
        "citation_applicable": citation_applicable,
        "source_available": source_available,
        "source_count": len(sources),
        "unsupported_expected": unsupported_expected,
        "unsupported_detected": not_found,
        "passed": test_pass,
        "latency_seconds": round(latency, 3),
        "failure_reasons": [
            name for name, passed in checks.items() if not passed
        ],
    }


def run_evaluation():
    test_cases = load_test_cases()
    results = []

    for index, test_case in enumerate(test_cases, start=1):
        result = evaluate_test_case(index, test_case)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] Test {index}: {result['question']}")
        print(
            f"  Route: {result['actual_route']} "
            f"(expected: {result['expected_route']})"
        )
        print(
            f"  Keywords: {result['keyword_check']} | "
            f"Citation: {result['citation_present']} | "
            f"Sources: {result['source_count']} | "
            f"Security: {result['security_check']} | "
            f"Unsupported handling: "
            f"{result['unsupported_question_check']}"
        )
        print(f"  Latency: {result['latency_seconds']} seconds")

        if result["failure_reasons"]:
            print(
                "  Failed checks: "
                + ", ".join(result["failure_reasons"])
            )

    total = len(results)
    passed = sum(result["passed"] for result in results)
    latencies = [result["latency_seconds"] for result in results]

    route_correct = sum(result["route_check"] for result in results)
    citation_applicable_results = [
        result for result in results if result["citation_applicable"]
    ]
    retrieval_applicable_results = [
        result for result in results if result["unsupported_expected"] is False
        and result["actual_route"] == "rag"
        and not result["unsupported_detected"]
    ]

    summary = {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "score_percent": round(passed / total * 100, 2) if total else 0,
        "route_accuracy_percent": round(
            route_correct / total * 100, 2
        ) if total else 0,
        "citation_presence_percent": round(
            sum(r["citation_present"] for r in citation_applicable_results)
            / len(citation_applicable_results) * 100, 2
        ) if citation_applicable_results else None,
        "source_availability_percent": round(
            sum(r["source_available"] for r in retrieval_applicable_results)
            / len(retrieval_applicable_results) * 100, 2
        ) if retrieval_applicable_results else None,
        "average_latency_seconds": round(mean(latencies), 3) if latencies else 0,
        "max_latency_seconds": round(max(latencies), 3) if latencies else 0,
        "results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Score: {summary['score_percent']:.2f}%")
    print(f"Route accuracy: {summary['route_accuracy_percent']:.2f}%")
    print(
        "Citation presence: "
        f"{summary['citation_presence_percent']}"
    )
    print(
        "Source availability: "
        f"{summary['source_availability_percent']}"
    )
    print(
        "Average latency: "
        f"{summary['average_latency_seconds']} seconds"
    )
    print(
        "Maximum latency: "
        f"{summary['max_latency_seconds']} seconds"
    )
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
