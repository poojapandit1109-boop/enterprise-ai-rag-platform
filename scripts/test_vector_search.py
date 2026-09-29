from app.vector_search import semantic_search


def main():
    query = "How does the system retrieve information?"

    results = semantic_search(
        query,
        top_k=3,
    )

    print("Query:", query)
    print("Results found:", len(results))

    for i, result in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print("Chunk ID:", result["chunk_id"])
        print("Document ID:", result["document_id"])
        print("Chunk Index:", result["chunk_index"])
        print("Filename:", result["filename"])
        print("Title:", result["title"])
        print("Distance:", round(result["distance"], 4))
        print("Content:", result["content"])


if __name__ == "__main__":
    main()