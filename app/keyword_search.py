from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Document, DocumentChunk


def keyword_search(
    query: str,
    top_k: int = 3,
):
    db = SessionLocal()

    try:
        # Convert the user's query into a PostgreSQL full-text query
        search_query = func.websearch_to_tsquery(
            "english",
            query,
        )

        # Convert document chunks into searchable text vectors
        document_vector = func.to_tsvector(
            "english",
            DocumentChunk.content,
        )

        # Calculate keyword relevance
        rank = func.ts_rank_cd(
            document_vector,
            search_query,
        )

        statement = (
            select(
                DocumentChunk,
                Document.filename,
                Document.title,
                rank.label("rank"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                document_vector.op("@@")(search_query)
            )
            .order_by(
                rank.desc()
            )
            .limit(top_k)
        )

        rows = db.execute(statement).all()

        results = []

        for chunk, filename, title, rank_value in rows:
            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "filename": filename,
                    "title": title,
                    "content": chunk.content,
                    "rank": float(rank_value),
                }
            )

        return results

    finally:
        db.close()