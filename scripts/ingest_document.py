from app.database import SessionLocal
from app.models import Document, DocumentChunk
from app.pdf_loader import extract_text_from_pdf
from app.chunker import chunk_text


PDF_PATH = "data/documents/sample pdf.pdf"


def main():
    text = extract_text_from_pdf(PDF_PATH)

    chunks = chunk_text(
        text,
        chunk_size=30,
        chunk_overlap=5,
    )

    db = SessionLocal()

    document = Document(
        filename="sample pdf.pdf",
        title="Enterprise AI Knowledge Platform",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    for index, chunk in enumerate(chunks):
        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
        )

        db.add(document_chunk)

    db.commit()

    print(f"Document ID: {document.id}")
    print(f"Number of chunks stored: {len(chunks)}")

    db.close()


if __name__ == "__main__":
    main()