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
) -> dict:
    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError("No text could be extracted from the PDF.")

    # Step 2: Split text into chunks
    chunks = chunk_text(
        text,
        chunk_size=30,
        chunk_overlap=5,
    )

    if not chunks:
        raise ValueError("No chunks were created from the PDF.")

    db = SessionLocal()

    try:
        # Step 3: Check whether the document already exists
        existing_document = (
            db.query(Document)
            .filter(Document.filename == filename)
            .first()
        )

        if existing_document:
            document = existing_document

            # Remove old chunks before re-ingesting
            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).delete()

        else:
            # Step 4: Create document record
            document = Document(
                filename=filename,
                title=title or Path(filename).stem,
            )

            db.add(document)
            db.commit()
            db.refresh(document)

        # Step 5: Generate embeddings for chunks
        embeddings = model.encode(
            chunks,
            normalize_embeddings=True,
        )

        # Step 6: Store chunks + embeddings
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
            "chunks_created": len(chunks),
            "message": "Document ingested successfully",
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()