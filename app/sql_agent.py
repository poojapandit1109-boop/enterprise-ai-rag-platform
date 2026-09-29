from app.sql_tools import execute_sql_tool


def run_sql_agent(question: str) -> dict:
    """
    Rule-based SQL Agent.

    Selects a safe, predefined SQL tool based
    on the user's natural-language question and
    converts the database result into a user-friendly answer.
    """

    question_lower = question.lower().strip()

    # --------------------------------------------------
    # Document count
    # --------------------------------------------------

    document_count_phrases = [
        "how many documents",
        "number of documents",
        "document count",
        "total documents",
        "total number of documents",
        "how many files",
        "number of files",
        "total files",
        "how many documents are stored",
        "how many documents are there",
    ]

    if any(
        phrase in question_lower
        for phrase in document_count_phrases
    ):
        result = execute_sql_tool(
            "database_summary"
        )

        document_count = result["document_count"]

        if document_count == 1:
            answer = (
                "There is 1 document currently stored "
                "in the knowledge base."
            )
        else:
            answer = (
                f"There are {document_count} documents "
                "currently stored in the knowledge base."
            )

        return {
            "question": question,
            "tool": "database_summary",
            "answer": answer,
            "result": {
                "document_count": document_count
            },
        }

    # --------------------------------------------------
    # Chunk count
    # --------------------------------------------------

    chunk_count_phrases = [
        "how many chunks",
        "number of chunks",
        "chunk count",
        "total chunks",
        "total number of chunks",
        "how many text chunks",
    ]

    if any(
        phrase in question_lower
        for phrase in chunk_count_phrases
    ):
        result = execute_sql_tool(
            "database_summary"
        )

        chunk_count = result["chunk_count"]

        if chunk_count == 1:
            answer = (
                "There is 1 text chunk currently "
                "stored in the knowledge base."
            )
        else:
            answer = (
                f"There are {chunk_count} text chunks "
                "currently stored in the knowledge base."
            )

        return {
            "question": question,
            "tool": "database_summary",
            "answer": answer,
            "result": {
                "chunk_count": chunk_count
            },
        }

    # --------------------------------------------------
    # List documents
    # --------------------------------------------------

    list_document_phrases = [
        "list documents",
        "list the documents",
        "which documents",
        "what documents",
        "show documents",
        "show me the documents",
        "available documents",
        "available files",
        "what files",
        "which files",
        "show files",
        "show me all available files",
    ]

    if any(
        phrase in question_lower
        for phrase in list_document_phrases
    ):
        result = execute_sql_tool(
            "list_documents"
        )

        documents = result

        if not documents:
            answer = (
                "There are currently no documents "
                "stored in the knowledge base."
            )

        else:
            document_lines = []

            for document in documents:
                title = document["title"]
                filename = document["filename"]

                document_lines.append(
                    f"- {title} ({filename})"
                )

            answer = (
                f"The knowledge base contains "
                f"{len(documents)} document(s):\n"
                + "\n".join(document_lines)
            )

        return {
            "question": question,
            "tool": "list_documents",
            "answer": answer,
            "result": documents,
        }

    # --------------------------------------------------
    # No matching SQL tool
    # --------------------------------------------------

    return {
        "question": question,
        "tool": None,
        "answer": None,
        "result": None,
        "message": "No SQL tool matched this question.",
    }