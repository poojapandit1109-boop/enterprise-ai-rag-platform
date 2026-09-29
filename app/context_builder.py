def build_context(results: list[dict]) -> str:
    if not results:
        return "No relevant information was found."

    context_parts = []

    for i, result in enumerate(results, start=1):
        source = result["title"] or result["filename"]

        context_parts.append(
            f"[Source {i}]\n"
            f"Document: {source}\n"
            f"Chunk: {result['chunk_index']}\n"
            f"Content:\n{result['content']}"
        )

    return "\n\n".join(context_parts)