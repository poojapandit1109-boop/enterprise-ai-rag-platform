from app.hybrid_search import hybrid_search


def main():
    query = "prompt injection"

    results = hybrid_search(
        query,
        top_k=3,
    )

    print("\n==============================")
    print("HYBRID SEARCH RESULTS")
    print("==============================")

    for result in results:
        print("\n--- Result ---")
        print("Document ID:", result["document_id"])
        print("Filename:", result["filename"])
        print("Title:", result["title"])
        print("Chunk:", result["chunk_index"])
        print("Fusion Score:", round(result["fusion_score"], 6))
        print("Content:", result["content"])


if __name__ == "__main__":
    main()