from sentence_transformers import SentenceTransformer

from app.database import SessionLocal
from app.models import DocumentChunk


MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    db = SessionLocal()

    chunks = db.query(DocumentChunk).all()

    print(f"Found {len(chunks)} chunks in database.")

    for chunk in chunks:
        print(f"Generating embedding for chunk {chunk.id}...")

        embedding = model.encode(
            chunk.content,
            normalize_embeddings=True,
        )

        chunk.embedding = embedding.tolist()

    db.commit()

    print("All embeddings stored successfully.")

    db.close()


if __name__ == "__main__":
    main()