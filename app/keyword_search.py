from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Document, DocumentChunk


def keyword_search(
    query: str,
    top_k: int = 3,
    department: str | None = None,
    document_type: str | None = None,
):
    """
    Perform PostgreSQL full-text keyword search.

    Optional metadata filters restrict results by
    department and/or document type.
    """

    db = SessionLocal()

    try:
        search_query = func.websearch_to_tsquery(
            "english",
            query,
        )

        document_vector = func.to_tsvector(
            "english",
            DocumentChunk.content,
        )

        rank = func.ts_rank_cd(
            document_vector,
            search_query,
        )

        statement = (
            select(
                DocumentChunk,
                Document.filename,
                Document.title,
                Document.department,
                Document.document_type,
                rank.label("rank"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                document_vector.op("@@")(search_query)
            )
        )

        # ---------------------------------------------
        # Optional department filter
        # ---------------------------------------------

        if department:
            statement = statement.where(
                Document.department == department
            )

        # ---------------------------------------------
        # Optional document type filter
        # ---------------------------------------------

        if document_type:
            statement = statement.where(
                Document.document_type == document_type
            )

        statement = (
            statement
            .order_by(rank.desc())
            .limit(top_k)
        )

        rows = db.execute(statement).all()

        results = []

        for (
            chunk,
            filename,
            title,
            department_value,
            document_type_value,
            rank_value,
        ) in rows:
            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "filename": filename,
                    "title": title,
                    "department": department_value,
                    "document_type": document_type_value,
                    "content": chunk.content,
                    "rank": float(rank_value),
                }
            )

        return results

    finally:
        db.close()