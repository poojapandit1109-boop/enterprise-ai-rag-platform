from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from app.ingestion_service import ingest_pdf
from app.orchestrator import process_question


app = FastAPI(
    title="Enterprise AI RAG Platform",
    description="Enterprise RAG and AI Agent Platform",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


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
    )


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
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
    )

    return result