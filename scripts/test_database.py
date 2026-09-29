from app.database import SessionLocal
from app.models import Document, DocumentChunk


def main():
    db = SessionLocal()

    document = Document(
        filename="sample.pdf",
        title="Sample Enterprise Document",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="This is a sample document chunk for testing our RAG platform.",
    )

    db.add(chunk)
    db.commit()

    print(f"Document created with ID: {document.id}")
    print(f"Chunk created for document ID: {document.id}")

    db.close()


if __name__ == "__main__":
    main()