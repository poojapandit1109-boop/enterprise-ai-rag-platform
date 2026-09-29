from app.database import SessionLocal
from app.models import Document, DocumentChunk


def main():
    db = SessionLocal()

    documents = db.query(Document).all()

    print(f"Total documents: {len(documents)}")

    for document in documents:
        print("\n==============================")
        print(f"Document ID: {document.id}")
        print(f"Filename: {document.filename}")
        print(f"Title: {document.title}")

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        print(f"Number of chunks: {len(chunks)}")

        for chunk in chunks:
            print(f"\n--- Chunk {chunk.chunk_index + 1} ---")
            print(chunk.content)

    db.close()


if __name__ == "__main__":
    main()