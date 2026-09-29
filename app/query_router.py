def route_query(question: str) -> str:
    """
    Route a user question to the appropriate agent.
    """

    question_lower = question.lower().strip()

    sql_keywords = [
        # Document count
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

        # Chunk count
        "how many chunks",
        "number of chunks",
        "chunk count",
        "total chunks",
        "total number of chunks",
        "how many text chunks",

        # Document listing
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
    ]

    for keyword in sql_keywords:
        if keyword in question_lower:
            return "sql"

    return "rag"