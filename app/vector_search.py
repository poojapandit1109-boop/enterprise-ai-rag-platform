from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Document, DocumentChunk


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def semantic_search(
    query: str,
    top_k: int = 3,
    department: str | None = None,
    document_type: str | None = None,
):
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    db = SessionLocal()

    try:
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding.tolist()
        )

        statement = (
            select(
                DocumentChunk,
                Document.filename,
                Document.title,
                Document.department,
                Document.document_type,
                distance.label("distance"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
        )

        # Optional department filter
        if department:
            statement = statement.where(
                Document.department == department
            )

        # Optional document type filter
        if document_type:
            statement = statement.where(
                Document.document_type == document_type
            )

        statement = (
            statement
            .order_by(distance)
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
            distance_value,
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
                    "distance": float(distance_value),
                }
            )

        return results

    finally:
        db.close()