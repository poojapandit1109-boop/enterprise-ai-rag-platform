from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

print("Loading reranker model...")

reranker_model = CrossEncoder(MODEL_NAME)


def rerank_results(
    query: str,
    results: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Rerank retrieved documents using a CrossEncoder.

    The CrossEncoder evaluates the query and each
    retrieved chunk together and assigns a relevance score.
    """

    if not results:
        return []

    pairs = [
        (
            query,
            result["content"],
        )
        for result in results
    ]

    scores = reranker_model.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):
        updated_result = result.copy()

        updated_result["reranker_score"] = float(score)

        reranked_results.append(updated_result)

    reranked_results.sort(
        key=lambda item: item["reranker_score"],
        reverse=True,
    )

    return reranked_results[:top_k]