# Enterprise AI RAG Platform

An enterprise-oriented Retrieval-Augmented Generation (RAG) platform built with Python, FastAPI, PostgreSQL, and pgvector. It ingests PDF documents, retrieves relevant information, reranks results, and generates answers grounded in retrieved context with source citations.

## Architecture

```mermaid
flowchart TD
    A[User] --> B[FastAPI Application]
    B --> C[Query Router]
    C --> D[Prompt Injection Detection]
    D --> E[Hybrid Retrieval]
    E --> F[PostgreSQL + pgvector]
    E --> G[Cross-Encoder Reranker]
    G --> H[Local Language Model]
    H --> I[Answer with Source Citations]
    J[PDF Upload] --> K[Document Processing]
    K --> L[Text Chunking]
    L --> M[Embedding Generation]
    M --> F
```

For detailed system architecture and technology decisions, see [Detailed RAG Architecture](architecture/rag_architecture.md).

## Key Features

- PDF document ingestion and text chunking
- Embedding generation with Sentence Transformers
- PostgreSQL storage with pgvector
- Hybrid retrieval and Cross-Encoder reranking
- Local language model integration
- Answers with source citations
- Department and document-type metadata filtering
- SQL Agent for supported database questions
- Query routing and prompt injection detection
- Evaluation harness and automated tests
- FastAPI endpoints and Docker-based API deployment

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| Database | PostgreSQL |
| Vector search | pgvector |
| Embeddings | Sentence Transformers |
| Reranking | Cross-Encoder |
| Language model | FLAN-T5 Small |
| Database access | SQLAlchemy and Psycopg |
| Containerization | Docker |
| Testing | Pytest |

## Project Structure

```text
enterprise-ai-rag-platform/
+-- app/
¦   +-- chunker.py
¦   +-- context_builder.py
¦   +-- database.py
¦   +-- hybrid_search.py
¦   +-- ingestion_service.py
¦   +-- keyword_search.py
¦   +-- main.py
¦   +-- orchestrator.py
¦   +-- pdf_loader.py
¦   +-- query_router.py
¦   +-- rag_service.py
¦   +-- reranker.py
¦   +-- security.py
¦   +-- sql_agent.py
¦   +-- vector_search.py
+-- architecture/
¦   +-- rag_architecture.md
+-- data/
+-- evaluation/
¦   +-- evaluation_results.json
+-- notebooks/
+-- scripts/
¦   +-- run_evaluation.py
¦   +-- run_tests_windows.py
+-- tests/
¦   +-- test_api.py
+-- .env.example
+-- .gitignore
+-- api-openapi.json
+-- docker-compose.yml
+-- Dockerfile
+-- requirements.txt
+-- README.md
```

## Prerequisites

- Python compatible with the project dependencies
- Git
- Docker Desktop
- PostgreSQL with the pgvector extension
- A configured database and valid credentials

**Important:** Docker Compose starts the API service only. PostgreSQL runs separately and must already be available on port `5432`.

## Getting Started

### 1. Clone the repository

```powershell
git clone https://github.com/poojapandit1109-boop/enterprise-ai-rag-platform.git
cd enterprise-ai-rag-platform
```

If you have already cloned the repository, open PowerShell in the project directory instead.

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If script activation is blocked, use the virtual environment's Python executable directly:

```powershell
venv\Scripts\python.exe --version
```

### 3. Install dependencies

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Configure `DATABASE_URL` in `.env` for your environment. Example format:

```text
APP_NAME=Enterprise AI RAG Platform
ENVIRONMENT=development
LLM_API_KEY=
DATABASE_URL=postgresql+psycopg://ai_user:YOUR_PASSWORD@localhost:5432/enterprise_ai
```

Replace the example password and database details with your actual configuration. URL-encode special characters in passwords when necessary.

**Never commit `.env` or real credentials to GitHub.** Keep `.env.example` limited to safe placeholders. The local language model may not require a hosted API key.

### 5. Start the services

Ensure Docker Desktop is running and PostgreSQL with pgvector is available.

Check running containers:

```powershell
docker ps
```

Start the API service when needed:

```powershell
docker compose up -d
```

The Compose configuration starts the API only; it does not create or manage the PostgreSQL container.

### 6. Check API health

```powershell
curl.exe http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## API Documentation

When the API is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI specification: [`api-openapi.json`](api-openapi.json)

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Welcome endpoint |
| GET | `/health` | Health check |
| POST | `/ask` | Ask a question against the knowledge base |
| POST | `/documents/upload` | Upload a document |

### Ask a question

Example using PowerShell:

```powershell
$body = @{
    question = "What does the architecture document explain?"
    top_k = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -ContentType "application/json" -Body $body
```

### Upload a PDF

Replace the example file path with a real PDF path:

```powershell
curl.exe -X POST "http://localhost:8000/documents/upload" -F "file=@C:\path\to\document.pdf" -F "title=Architecture Guide" -F "department=Engineering" -F "document_type=Architecture"
```

## Testing

### Run the API tests on Windows

The project includes a helper that reads `DATABASE_URL` from `.env` and uses `localhost` for the Windows test process. It does not modify `.env`.

Run from the repository root:

```powershell
venv\Scripts\python.exe scripts\run_tests_windows.py
```

The API test suite has previously completed with **11 passed, 0 failed**. Two deprecation warnings were reported by Starlette/AnyIO; these did not cause test failures.

### Run tests directly

```powershell
venv\Scripts\python.exe -m pytest -q
```

Ensure PostgreSQL is running and the test process has a valid `DATABASE_URL`. Tests outside the Windows helper may need the database host configured for the environment where Python is running.

## Evaluation

Run the evaluation script from the repository root:

```powershell
venv\Scripts\python.exe scripts\run_evaluation.py
```

The evaluation report is saved under `evaluation/evaluation_results.json`. Running the evaluation again updates that report, so review the results before committing changes.

The current committed evaluation report records **15 of 15 configured test cases passing (100%)**, with zero failed cases. The configured checks cover query routing, citation presence and validity, cited-source content, source availability, security handling, unsupported-question handling, and response latency.

The report records an average latency of `0.101` seconds and a maximum latency of `0.412` seconds for that evaluation run. These measurements are specific to the tested environment and cases.

This is a small development evaluation set. It does not guarantee production performance, answer quality, or security.

## Security Considerations

- Keep credentials in `.env` and out of version control.
- Treat uploaded documents and retrieved text as untrusted input.
- Add authentication and authorization before exposing enterprise documents.
- Treat prompt injection detection as one layer of defense, not a complete security solution.
- Add rate limiting, monitoring, and secure deployment configuration before production use.

## Current Limitations

- Evaluation coverage is limited.
- Retrieval quality depends on document quality, chunking, embeddings, and query formulation.
- Local model performance depends on available hardware.
- PostgreSQL must be configured and running separately.
- Production deployment requires additional security, observability, scaling, and reliability work.

## Future Improvements

- Expand evaluation datasets and retrieval metrics.
- Add authentication and role-based access control.
- Improve document parsing and chunking.
- Add tracing and performance monitoring.
- Add continuous integration and automated deployment.
- Evaluate alternative embedding and language models.

## Project Status

This is a portfolio and development project demonstrating an end-to-end RAG workflow. Re-run tests and evaluations before making performance claims.

## Author

**GitHub:** [poojapandit1109-boop](https://github.com/poojapandit1109-boop)

