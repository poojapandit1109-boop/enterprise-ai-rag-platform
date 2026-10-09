import json
import time
from pathlib import Path

from app.orchestrator import process_question


BASE_DIR = Path(__file__).resolve().parent.parent
TEST_CASES_FILE = BASE_DIR / "evaluation" / "test_cases.json"


def load_test_cases():
    with open(
        TEST_CASES_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def check_keywords(
    answer: str,
    expected_keywords: list[str],
) -> bool:
    answer_lower = answer.lower()

    return all(
        keyword.lower() in answer_lower
        for keyword in expected_keywords
    )


def run_evaluation():
    test_cases = load_test_cases()

    results = []

    passed = 0

    for index, test_case in enumerate(
        test_cases,
        start=1,
    ):
        question = test_case["question"]

        expected_keywords = test_case[
            "expected_keywords"
        ]

        expected_route = test_case[
            "expected_route"
        ]

        start_time = time.perf_counter()

        response = process_question(
            question=question,
            top_k=3,
        )

        latency = (
            time.perf_counter() - start_time
        )

        actual_route = response.get(
            "route"
        )

        result = response.get(
            "result"
        )

        if actual_route == "blocked":
            answer = result.get(
                "message",
                "blocked",
            )
        elif result:
            answer = result.get(
                "answer"
            ) or result.get(
                "message",
                "",
            )
        else:
            answer = ""

        keyword_pass = check_keywords(
            answer,
            expected_keywords,
        )

        route_pass = (
            actual_route == expected_route
        )

        test_pass = (
            keyword_pass
            and route_pass
        )

        if test_pass:
            passed += 1

        results.append(
            {
                "test_case": index,
                "question": question,
                "expected_route": expected_route,
                "actual_route": actual_route,
                "keyword_check": keyword_pass,
                "route_check": route_pass,
                "passed": test_pass,
                "latency_seconds": round(
                    latency,
                    3,
                ),
            }
        )

        status = "PASS" if test_pass else "FAIL"

        print(
            f"[{status}] Test {index}: "
            f"{question}"
        )

        print(
            f"      Route: "
            f"{actual_route}"
        )

        print(
            f"      Latency: "
            f"{latency:.3f}s"
        )

        print()

    total = len(test_cases)

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"Passed: {passed}/{total}"
    )

    print(
        f"Evaluation Score: "
        f"{accuracy:.2f}%"
    )

    print("=" * 60)

    output_file = (
        BASE_DIR
        / "evaluation"
        / "evaluation_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "total_tests": total,
                "passed_tests": passed,
                "score_percent": round(
                    accuracy,
                    2,
                ),
                "results": results,
            },
            file,
            indent=2,
        )

    print(
        f"Results saved to: "
        f"{output_file}"
    )


if __name__ == "__main__":
    run_evaluation()