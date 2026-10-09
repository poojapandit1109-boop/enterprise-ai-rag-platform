from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.chunker import chunk_text
from app.database import SessionLocal
from app.models import Document, DocumentChunk
from app.pdf_loader import extract_text_from_pdf


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def ingest_pdf(
    file_path: str,
    filename: str,
    title: str | None = None,
    department: str | None = None,
    document_type: str | None = None,
) -> dict:
    """
    Ingest a PDF document into the enterprise knowledge base.

    The document is:
    1. Read from the PDF.
    2. Split into chunks.
    3. Converted into embeddings.
    4. Stored in PostgreSQL.
    5. Associated with enterprise metadata.
    """

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from the PDF."
        )

    chunks = chunk_text(
        text,
        chunk_size=30,
        chunk_overlap=5,
    )

    if not chunks:
        raise ValueError(
            "No chunks were created from the PDF."
        )

    db = SessionLocal()

    try:
        existing_document = (
            db.query(Document)
            .filter(Document.filename == filename)
            .first()
        )

        if existing_document:
            document = existing_document

            document.title = (
                title
                or document.title
                or Path(filename).stem
            )

            document.department = department
            document.document_type = document_type

            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).delete()

        else:
            document = Document(
                filename=filename,
                title=title or Path(filename).stem,
                department=department,
                document_type=document_type,
            )

            db.add(document)
            db.commit()
            db.refresh(document)

        embeddings = model.encode(
            chunks,
            normalize_embeddings=True,
        )

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding.tolist(),
            )

            db.add(document_chunk)

        db.commit()

        return {
            "document_id": document.id,
            "filename": filename,
            "title": document.title,
            "department": document.department,
            "document_type": document.document_type,
            "chunks_created": len(chunks),
            "message": "Document ingested successfully",
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()