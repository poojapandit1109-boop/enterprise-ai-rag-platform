import logging
import time

from app.query_router import route_query
from app.sql_agent import run_sql_agent
from app.rag_service import generate_answer
from app.security import detect_prompt_injection


logger = logging.getLogger(__name__)


def process_question(
    question: str,
    top_k: int = 3,
    department: str | None = None,
    document_type: str | None = None,
) -> dict:
    """
    Route a user question to the appropriate agent
    after performing a security check.

    Records basic observability information including
    route and request latency.
    """

    start_time = time.perf_counter()

    logger.info(
        "Question received | question=%s",
        question,
    )

    if detect_prompt_injection(question):
        latency = time.perf_counter() - start_time

        logger.warning(
            "Request blocked | reason=prompt_injection | "
            "latency=%.3fs",
            latency,
        )

        return {
            "question": question,
            "route": "blocked",
            "result": {
                "status": "blocked",
                "message": (
                    "The request was blocked because it "
                    "contains a potentially unsafe instruction."
                ),
            },
        }

    route = route_query(question)

    logger.info(
        "Query routed | route=%s",
        route,
    )

    if route == "sql":
        result = run_sql_agent(question)

        latency = time.perf_counter() - start_time

        logger.info(
            "SQL request completed | latency=%.3fs",
            latency,
        )

        return {
            "question": question,
            "route": "sql",
            "result": result,
        }

    if route == "rag":
        result = generate_answer(
            question=question,
            top_k=top_k,
            department=department,
            document_type=document_type,
        )

        latency = time.perf_counter() - start_time

        logger.info(
            "RAG request completed | latency=%.3fs",
            latency,
        )

        return {
            "question": question,
            "route": "rag",
            "result": result,
        }

    latency = time.perf_counter() - start_time

    logger.error(
        "Unknown route | latency=%.3fs",
        latency,
    )

    return {
        "question": question,
        "route": "unknown",
        "result": None,
    }