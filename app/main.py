import logging
import os
import secrets
from pathlib import Path
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel, Field

from app.logging_config import configure_logging
from app.ingestion_service import ingest_pdf
from app.orchestrator import process_question


configure_logging()
logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
UPLOAD_DIR = Path("data/documents")
UPLOAD_CHUNK_BYTES = 64 * 1024

app = FastAPI(
    title="Enterprise AI RAG Platform",
    description="Enterprise RAG and AI Agent Platform",
    version="1.0.0",
)


def require_api_key(
    api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    expected_key = os.getenv("API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=10)
    department: str | None = Field(default=None, max_length=100)
    document_type: str | None = Field(default=None, max_length=100)


@app.get("/")
def home():
    return {"message": "Enterprise AI RAG Platform is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ask", dependencies=[Depends(require_api_key)])
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question must not be blank.",
        )

    return process_question(
        question=question,
        top_k=request.top_k,
        department=request.department,
        document_type=request.document_type,
    )


@app.post(
    "/documents/upload",
    dependencies=[Depends(require_api_key)],
)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    department: str | None = Form(default=None),
    document_type: str | None = Form(default=None),
):
    # Handle both Windows and Linux path separators.
    original_name = (
        (file.filename or "")
        .replace("\\", "/")
        .split("/")[-1]
        .strip()
    )

    if not original_name or original_name in (".", ".."):
        raise HTTPException(
            status_code=400,
            detail="A valid filename is required.",
        )

    if not original_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are accepted.",
        )

    if file.content_type not in (
        "application/pdf",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=415,
            detail="The uploaded file must be a PDF.",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Never trust the client-provided filename for storage.
    safe_filename = f"{uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / safe_filename
    total_bytes = 0

    try:
        with file_path.open("wb") as output_file:
            while True:
                chunk = await file.read(UPLOAD_CHUNK_BYTES)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF must be 10 MB or smaller.",
                    )

                output_file.write(chunk)

        if total_bytes == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        # Validate the PDF signature before ingestion.
        with file_path.open("rb") as uploaded_file:
            pdf_signature = uploaded_file.read(5)

        if pdf_signature != b"%PDF-":
            raise HTTPException(
                status_code=415,
                detail="The file does not have a valid PDF signature.",
            )

        return ingest_pdf(
            file_path=str(file_path),
            filename=original_name,
            title=title,
            department=department,
            document_type=document_type,
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Document ingestion failed")
        raise HTTPException(
            status_code=500,
            detail="The document could not be processed.",
        ) from exc

    finally:
        await file.close()

        try:
            if file_path.exists():
                os.remove(file_path)
        except OSError:
            logger.exception("Could not remove temporary upload file")
