from app.keyword_search import keyword_search
from app.vector_search import semantic_search


def hybrid_search(
    query: str,
    top_k: int = 3,
    department: str | None = None,
    document_type: str | None = None,
):
    """
    Perform hybrid retrieval using:

    1. Semantic vector search
    2. Keyword search
    3. Reciprocal Rank Fusion

    Optional metadata filters can restrict results
    by department and/or document type.
    """

    vector_results = semantic_search(
        query,
        top_k=top_k,
        department=department,
        document_type=document_type,
    )

    keyword_results = keyword_search(
        query,
        top_k=top_k,
        department=department,
        document_type=document_type,
    )

    fusion_scores = {}
    result_lookup = {}

    vector_metadata = {}

    # ---------------------------------------------
    # Add semantic search results
    # ---------------------------------------------

    for rank, result in enumerate(
        vector_results,
        start=1,
    ):
        chunk_id = result["chunk_id"]

        fusion_scores[chunk_id] = (
            fusion_scores.get(chunk_id, 0)
            + 1 / (60 + rank)
        )

        vector_metadata[chunk_id] = {
            "vector_distance": result["distance"],
        }

        result_lookup[chunk_id] = result.copy()

    # ---------------------------------------------
    # Add keyword search results
    # ---------------------------------------------

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):
        chunk_id = result["chunk_id"]

        fusion_scores[chunk_id] = (
            fusion_scores.get(chunk_id, 0)
            + 1 / (60 + rank)
        )

        if chunk_id not in result_lookup:
            result_lookup[chunk_id] = result.copy()

    # ---------------------------------------------
    # Rank using fusion score
    # ---------------------------------------------

    ranked_chunk_ids = sorted(
        fusion_scores,
        key=fusion_scores.get,
        reverse=True,
    )

    results = []

    for chunk_id in ranked_chunk_ids[:top_k]:
        result = result_lookup[chunk_id].copy()

        result["fusion_score"] = fusion_scores[chunk_id]

        result["vector_distance"] = vector_metadata.get(
            chunk_id,
            {},
        ).get("vector_distance")

        result["keyword_match"] = any(
            keyword_result["chunk_id"] == chunk_id
            for keyword_result in keyword_results
        )

        results.append(result)

    return results