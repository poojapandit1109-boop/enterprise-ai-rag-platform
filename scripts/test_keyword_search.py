from app.keyword_search import keyword_search


def main():
    query = "prompt injection"

    results = keyword_search(
        query,
        top_k=3,
    )

    print("\n==============================")
    print("KEYWORD SEARCH RESULTS")
    print("==============================")

    for result in results:
        print("\n--- Result ---")
        print("Document ID:", result["document_id"])
        print("Filename:", result["filename"])
        print("Title:", result["title"])
        print("Chunk:", result["chunk_index"])
        print("Rank:", round(result["rank"], 4))
        print("Content:", result["content"])


if __name__ == "__main__":
    main()