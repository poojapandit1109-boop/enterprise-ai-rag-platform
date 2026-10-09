from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from app.logging_config import configure_logging
from app.ingestion_service import ingest_pdf
from app.orchestrator import process_question


configure_logging()


app = FastAPI(
    title="Enterprise AI RAG Platform",
    description="Enterprise RAG and AI Agent Platform",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3
    department: str | None = None
    document_type: str | None = None


@app.get("/")
def home():
    return {
        "message": "Enterprise AI RAG Platform is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    return process_question(
        question=request.question,
        top_k=request.top_k,
        department=request.department,
        document_type=request.document_type,
    )


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = None,
    department: str | None = None,
    document_type: str | None = None,
):
    documents_dir = Path("data/documents")

    documents_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = documents_dir / file.filename

    file_content = await file.read()

    with open(file_path, "wb") as output_file:
        output_file.write(file_content)

    result = ingest_pdf(
        file_path=str(file_path),
        filename=file.filename,
        title=title,
        department=department,
        document_type=document_type,
    )

    return result