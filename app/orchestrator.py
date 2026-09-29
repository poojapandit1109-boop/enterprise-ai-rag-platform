from app.query_router import route_query
from app.sql_agent import run_sql_agent
from app.rag_service import generate_answer
from app.security import detect_prompt_injection


def process_question(
    question: str,
    top_k: int = 3,
) -> dict:
    """
    Route a user question to the appropriate agent
    after performing a security check.
    """

    # Step 1: Security check
    if detect_prompt_injection(question):
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

    # Step 2: Route the question
    route = route_query(question)

    # Step 3: SQL Agent
    if route == "sql":
        result = run_sql_agent(question)

        return {
            "question": question,
            "route": "sql",
            "result": result,
        }

    # Step 4: RAG Agent
    if route == "rag":
        result = generate_answer(
            question=question,
            top_k=top_k,
        )

        return {
            "question": question,
            "route": "rag",
            "result": result,
        }

    return {
        "question": question,
        "route": "unknown",
        "result": None,
    }