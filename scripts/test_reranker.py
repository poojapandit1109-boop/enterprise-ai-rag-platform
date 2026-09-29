from app.hybrid_search import hybrid_search
from app.reranker import rerank_results


def main():
    query = "What security measures should enterprise AI systems use?"

    print("\nRunning hybrid search...")

    results = hybrid_search(
        query,
        top_k=5,
    )

    print(f"Hybrid results: {len(results)}")

    print("\nBefore reranking:")

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. "
            f"Chunk {result['chunk_index']} | "
            f"Fusion score: {result['fusion_score']:.6f}"
        )

    print("\nRunning reranker...")

    reranked_results = rerank_results(
        query=query,
        results=results,
        top_k=3,
    )

    print("\nAfter reranking:")

    for index, result in enumerate(
        reranked_results,
        start=1,
    ):
        print(
            f"{index}. "
            f"Chunk {result['chunk_index']} | "
            f"Reranker score: "
            f"{result['reranker_score']:.6f}"
        )

        print(
            f"   Content: {result['content']}"
        )


if __name__ == "__main__":
    main()