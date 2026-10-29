
import json
import os
import re
import time
from pathlib import Path
from statistics import mean

from dotenv import dotenv_values
from sqlalchemy.engine import make_url



BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
TEST_CASES_FILE = BASE_DIR / "evaluation" / "test_cases.json"
RESULTS_FILE = BASE_DIR / "evaluation" / "evaluation_results.json"

CITATION_PATTERN = re.compile(r"\[Source\s+(\d+)\]", re.IGNORECASE)


def configure_windows_database():
    """Use localhost for database access from the Windows host."""
    if not ENV_FILE.exists():
        raise FileNotFoundError(f".env file not found: {ENV_FILE}")

    database_url = dotenv_values(ENV_FILE).get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is missing from .env")

    url = make_url(database_url)
    if not url.host:
        raise ValueError("Database host is missing from DATABASE_URL")

    # Only change the host in this Python process.
    os.environ["DATABASE_URL"] = url.set(host="localhost").render_as_string(
        hide_password=False
    )


def load_test_cases():
    with TEST_CASES_FILE.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError("test_cases.json must contain a JSON list")

    return cases


def check_keywords(answer, keywords):
    answer_lower = (answer or "").lower()
    return all(str(word).lower() in answer_lower for word in keywords)


def check_expected_answer(answer, expected_values):
    if not expected_values:
        return None

    answer_lower = (answer or "").lower()
    return all(str(value).lower() in answer_lower for value in expected_values)


def validate_citations(answer, sources):
    numbers = [
        int(number)
        for number in CITATION_PATTERN.findall(answer or "")
    ]

    if not numbers:
        return {
            "citation_present": False,
            "references_valid": False,
            "source_content_valid": False,
            "citation_numbers": [],
        }

    references_valid = all(1 <= number <= len(sources) for number in numbers)

    source_content_valid = references_valid and all(
        isinstance(sources[number - 1], dict)
        and bool(
            sources[number - 1].get("content")
            or sources[number - 1].get("text")
        )
        for number in numbers
    )

    return {
        "citation_present": True,
        "references_valid": references_valid,
        "source_content_valid": source_content_valid,
        "citation_numbers": numbers,
    }


def evaluate_test_case(test_case, test_number):
    from app.orchestrator import process_question
    question = test_case["question"]
    expected_route = test_case.get("expected_route")
    expected_keywords = test_case.get("expected_keywords", [])
    expected_values = test_case.get("expected_answer_contains", [])
    expect_unsupported = test_case.get("expect_unsupported", False)

    started = time.perf_counter()

    try:
        response = process_question(question=question, top_k=3)
        latency = time.perf_counter() - started

        if not isinstance(response, dict):
            response = {}

        actual_route = response.get("route", "unknown")
        result = response.get("result", {})
        if not isinstance(result, dict):
            result = {}

        if actual_route == "blocked":
            answer = str(result.get("message", "") or "")
        else:
            answer = str(
                result.get("answer", result.get("message", "")) or ""
            )

        sources = result.get("sources", [])
        if not isinstance(sources, list):
            sources = []

        answer_lower = answer.lower()
        not_found = "not found" in answer_lower

        keyword_check = check_keywords(answer, expected_keywords)
        route_check = (
            actual_route == expected_route
            if expected_route is not None
            else True
        )

        retrieval_check = (
            (not sources if expect_unsupported and not_found else bool(sources))
            if actual_route == "rag"
            else True
        )

        citation_info = validate_citations(answer, sources)
        citation_applicable = actual_route == "rag" and not not_found

        citation_presence_check = (
            citation_info["citation_present"]
            if citation_applicable
            else True
        )
        citation_reference_check = (
            citation_info["references_valid"]
            if citation_applicable
            else True
        )
        cited_source_content_check = (
            citation_info["source_content_valid"]
            if citation_applicable
            else True
        )

        security_check = (
            actual_route == "blocked"
            if expected_route == "blocked"
            else None
        )

        unsupported_check = (
            actual_route == "rag" and not_found and not sources
            if expect_unsupported
            else None
        )

        expected_answer_check = check_expected_answer(answer, expected_values)

        checks = {
            "keyword_check": "PASS" if keyword_check else "FAIL",
            "route_check": "PASS" if route_check else "FAIL",
            "citation_presence_check": (
                "NOT APPLICABLE"
                if not citation_applicable
                else (
                    "PASS" if citation_presence_check else "FAIL"
                )
            ),
            "citation_reference_check": (
                "NOT APPLICABLE"
                if not citation_applicable
                else (
                    "PASS" if citation_reference_check else "FAIL"
                )
            ),
            "cited_source_content_check": (
                "NOT APPLICABLE"
                if not citation_applicable
                else (
                    "PASS" if cited_source_content_check else "FAIL"
                )
            ),
            "retrieval_check": "PASS" if retrieval_check else "FAIL",
            "security_check": (
                "NOT APPLICABLE"
                if security_check is None
                else ("PASS" if security_check else "FAIL")
            ),
            "unsupported_question_check": (
                "NOT APPLICABLE"
                if unsupported_check is None
                else ("PASS" if unsupported_check else "FAIL")
            ),
            "expected_answer_check": (
                "NOT APPLICABLE"
                if expected_answer_check is None
                else ("PASS" if expected_answer_check else "FAIL")
            ),
        }

        required_checks = [
            keyword_check,
            route_check,
            retrieval_check,
        ]

        if citation_applicable:
            required_checks.extend([
                citation_presence_check,
                citation_reference_check,
                cited_source_content_check,
            ])

        if security_check is not None:
            required_checks.append(security_check)

        if unsupported_check is not None:
            required_checks.append(unsupported_check)

        if expected_answer_check is not None:
            required_checks.append(expected_answer_check)

        return {
            "test_case": test_number,
            "question": question,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "answer": answer,
            "checks": checks,
            "keyword_check": keyword_check,
            "route_check": route_check,
            "citation_check": (
                "NOT APPLICABLE"
                if not citation_applicable
                else ("PASS" if citation_presence_check else "FAIL")
            ),
            "citation_reference_check": (
                "NOT APPLICABLE"
                if not citation_applicable
                else ("PASS" if citation_reference_check else "FAIL")
            ),
            "cited_source_content_check": (
                "NOT APPLICABLE"
                if not citation_applicable
                else ("PASS" if cited_source_content_check else "FAIL")
            ),
            "retrieval_check": retrieval_check,
            "security_check": checks["security_check"],
            "unsupported_question_check": checks["unsupported_question_check"],
            "expected_answer_check": checks["expected_answer_check"],
            "expected_answer_contains": expected_values,
            "citation_numbers": citation_info["citation_numbers"],
            "source_count": len(sources),
            "latency_seconds": round(latency, 3),
            "passed": all(required_checks),
            "error": None,
        }

    except Exception as exc:
        latency = time.perf_counter() - started
        error_checks = {
            "keyword_check": "FAIL",
            "route_check": "FAIL",
            "citation_presence_check": "FAIL",
            "citation_reference_check": "FAIL",
            "cited_source_content_check": "FAIL",
            "retrieval_check": "FAIL",
            "security_check": (
                "NOT APPLICABLE"
                if expected_route != "blocked"
                else "FAIL"
            ),
            "unsupported_question_check": (
                "FAIL" if expect_unsupported else "NOT APPLICABLE"
            ),
            "expected_answer_check": (
                "FAIL" if expected_values else "NOT APPLICABLE"
            ),
        }

        return {
            "test_case": test_number,
            "question": question,
            "expected_route": expected_route,
            "actual_route": "error",
            "answer": "",
            "checks": error_checks,
            "keyword_check": False,
            "route_check": False,
            "citation_check": "FAIL",
            "citation_reference_check": "FAIL",
            "cited_source_content_check": "FAIL",
            "retrieval_check": False,
            "security_check": error_checks["security_check"],
            "unsupported_question_check": error_checks[
                "unsupported_question_check"
            ],
            "expected_answer_check": error_checks["expected_answer_check"],
            "expected_answer_contains": expected_values,
            "citation_numbers": [],
            "source_count": 0,
            "latency_seconds": round(latency, 3),
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def percentage(passed, total):
    return round(100.0 * passed / total, 2) if total else 0.0


def check_pass_count(results, check_name):
    applicable = [
        item["checks"].get(check_name, "NOT APPLICABLE")
        for item in results
    ]
    applicable = [
        value for value in applicable
        if value != "NOT APPLICABLE"
    ]
    passed = sum(value == "PASS" for value in applicable)
    return passed, len(applicable)


def run_evaluation():
    configure_windows_database()
    test_cases = load_test_cases()
    results = []

    print(f"Running {len(test_cases)} evaluation tests...\n")

    for index, test_case in enumerate(test_cases, start=1):
        result = evaluate_test_case(test_case, index)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"[{status}] Test {index}: {result['question']} "
            f"({result['latency_seconds']}s)"
        )

        for check_name, check_status in result["checks"].items():
            print(f"    {check_name}: {check_status}")

        if result.get("error"):
            print(f"    error: {result['error']}")

    total = len(results)
    passed_tests = sum(item["passed"] for item in results)
    latencies = [item["latency_seconds"] for item in results]

    route_passes = sum(bool(item["route_check"]) for item in results)
    keyword_passes = sum(bool(item["keyword_check"]) for item in results)
    retrieval_passes = sum(bool(item["retrieval_check"]) for item in results)

    citation_presence_pass, citation_presence_total = check_pass_count(
        results, "citation_presence_check"
    )
    citation_reference_pass, citation_reference_total = check_pass_count(
        results, "citation_reference_check"
    )
    cited_content_pass, cited_content_total = check_pass_count(
        results, "cited_source_content_check"
    )
    security_pass, security_total = check_pass_count(results, "security_check")
    unsupported_pass, unsupported_total = check_pass_count(
        results, "unsupported_question_check"
    )
    exact_answer_pass, exact_answer_total = check_pass_count(
        results, "expected_answer_check"
    )

    summary = {
        "total_tests": total,
        "passed_tests": passed_tests,
        "failed_tests": total - passed_tests,
        "score_percent": percentage(passed_tests, total),
        "keyword_accuracy_percent": percentage(keyword_passes, total),
        "route_accuracy_percent": percentage(route_passes, total),
        "citation_presence_percent": percentage(
            citation_presence_pass, citation_presence_total
        ),
        "citation_reference_validity_percent": percentage(
            citation_reference_pass, citation_reference_total
        ),
        "cited_source_content_percent": percentage(
            cited_content_pass, cited_content_total
        ),
        "source_availability_percent": percentage(retrieval_passes, total),
        "security_pass_percent": percentage(security_pass, security_total),
        "unsupported_handling_pass_percent": percentage(
            unsupported_pass, unsupported_total
        ),
        "expected_answer_accuracy_percent": percentage(
            exact_answer_pass, exact_answer_total
        ),
        "expected_answer_tests": exact_answer_total,
        "average_latency_seconds": round(mean(latencies), 3) if latencies else 0,
        "max_latency_seconds": round(max(latencies), 3) if latencies else 0,
        "results": results,
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Overall score: {summary['score_percent']}%")
    print(f"Keyword accuracy: {summary['keyword_accuracy_percent']}%")
    print(f"Route accuracy: {summary['route_accuracy_percent']}%")
    print(
        "Citation reference validity: "
        f"{summary['citation_reference_validity_percent']}%"
    )
    print(
        "Exact-answer accuracy: "
        f"{summary['expected_answer_accuracy_percent']}% "
        f"({summary['expected_answer_tests']} applicable tests)"
    )
    print(f"Average latency: {summary['average_latency_seconds']}s")
    print(f"Maximum latency: {summary['max_latency_seconds']}s")
    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
