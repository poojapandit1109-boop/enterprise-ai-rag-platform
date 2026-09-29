from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Document, DocumentChunk


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def semantic_search(
    query: str,
    top_k: int = 3,
):
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    db = SessionLocal()

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding.tolist()
    )

    statement = (
        select(
            DocumentChunk,
            Document.filename,
            Document.title,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    rows = db.execute(statement).all()

    db.close()

    results = []

    for chunk, filename, title, distance_value in rows:
        results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "filename": filename,
                "title": title,
                "content": chunk.content,
                "distance": float(distance_value),
            }
        )

    return results