from sqlalchemy import text

from app.database import SessionLocal


def get_document_count() -> int:
    """
    Return the total number of documents stored
    in the database.
    """

    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT COUNT(*) FROM documents")
        )

        count = result.scalar()

        return int(count or 0)

    finally:
        db.close()


def get_chunk_count() -> int:
    """
    Return the total number of document chunks
    stored in the database.
    """

    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT COUNT(*) FROM document_chunks")
        )

        count = result.scalar()

        return int(count or 0)

    finally:
        db.close()


def get_database_summary() -> dict:
    """
    Return basic read-only database statistics.
    """

    return {
        "document_count": get_document_count(),
        "chunk_count": get_chunk_count(),
    }


def get_documents() -> list[dict]:
    """
    Return all documents stored in the database.
    """

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT
                    id,
                    filename,
                    title,
                    uploaded_at
                FROM documents
                ORDER BY id
            """)
        )

        rows = result.mappings().all()

        return [
            {
                "id": row["id"],
                "filename": row["filename"],
                "title": row["title"],
                "uploaded_at": str(row["uploaded_at"]),
            }
            for row in rows
        ]

    finally:
        db.close()