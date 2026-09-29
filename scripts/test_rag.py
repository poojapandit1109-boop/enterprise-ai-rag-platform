from app.rag_service import generate_answer


def main():
    question = "How does the system retrieve information?"

    result = generate_answer(
        question,
        top_k=3,
    )

    print("\n==============================")
    print("RAG ANSWER")
    print("==============================")
    print(result["answer"])

    print("\n==============================")
    print("SOURCES")
    print("==============================")

    for i, source in enumerate(result["sources"], start=1):
        print(f"\n--- Source {i} ---")
        print("Document ID:", source["document_id"])
        print("Filename:", source["filename"])
        print("Title:", source["title"])
        print("Chunk:", source["chunk_index"])
        print("Distance:", round(source["distance"], 4))


if __name__ == "__main__":
    main()