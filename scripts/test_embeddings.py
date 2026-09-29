from sentence_transformers import SentenceTransformer


def main():
    print("Loading embedding model...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    text = "Enterprise AI systems use retrieval augmented generation."

    embedding = model.encode(text)

    print("Embedding generated successfully!")
    print("Embedding dimensions:", len(embedding))
    print("First 10 values:", embedding[:10])


if __name__ == "__main__":
    main()