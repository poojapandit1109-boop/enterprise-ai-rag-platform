import json
import time
from pathlib import Path

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

    response = process_question(
        question=question,
        top_k=3,
    )

    latency = time.perf_counter() - start_time

    actual_route = response.get("route")
    result = response.get("result") or {}

    if actual_route == "blocked":
        answer = result.get("message", "blocked")
    else:
        answer = result.get("answer") or result.get("message", "")

    sources = result.get("sources", [])

    keyword_pass = check_keywords(
        answer,
        expected_keywords,
    )

    route_pass = actual_route == expected_route

    # Only require citations for RAG answers that claim
    # information was found in the documents.
    not_found = "not found" in answer.lower()

    citation_pass = (
        actual_route != "rag"
        or not_found
        or "[source" in answer.lower()
    )

    # A not-found answer is valid even when there are no sources.
    retrieval_pass = (
        actual_route != "rag"
        or not_found
        or len(sources) > 0
    )

    # Security cases must be blocked by the orchestrator.
    security_pass = (
        expected_route != "blocked"
        or actual_route == "blocked"
    )

    test_pass = all(
        [
            keyword_pass,
            route_pass,
            citation_pass,
            retrieval_pass,
            security_pass,
        ]
    )

    return {
        "test_case": index,
        "question": question,
        "expected_route": expected_route,
        "actual_route": actual_route,
        "keyword_check": keyword_pass,
        "route_check": route_pass,
        "citation_check": citation_pass,
        "retrieval_check": retrieval_pass,
        "security_check": security_pass,
        "source_count": len(sources),
        "passed": test_pass,
        "latency_seconds": round(latency, 3),
    }


def run_evaluation():
    test_cases = load_test_cases()
    results = []

    for index, test_case in enumerate(test_cases, start=1):
        result = evaluate_test_case(index, test_case)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"[{status}] Test {index}: "
            f"{result['question']}"
        )
        print(
            f"  Route: {result['actual_route']} "
            f"(expected: {result['expected_route']})"
        )
        print(
            f"  Keywords: {result['keyword_check']} | "
            f"Citations: {result['citation_check']} | "
            f"Sources: {result['source_count']} | "
            f"Security: {result['security_check']}"
        )
        print(
            f"  Latency: {result['latency_seconds']} seconds"
        )

    total = len(results)
    passed = sum(result["passed"] for result in results)
    score = passed / total * 100 if total else 0

    summary = {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,
        "score_percent": round(score, 2),
        "results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Score: {score:.2f}%")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
