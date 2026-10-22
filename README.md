# Enterprise AI RAG Platform

An enterprise-oriented Retrieval-Augmented Generation (RAG) platform that combines hybrid search, vector retrieval, reranking, a local language model, SQL-based document queries, and prompt-injection protection.

The project demonstrates an end-to-end approach to building an AI knowledge assistant that can answer questions from documents, route structured queries to a database, and return source information for document-grounded answers.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [API Examples](#api-examples)
- [Testing](#testing)
- [Evaluation](#evaluation)
- [Security Considerations](#security-considerations)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Project Status](#project-status)

## Overview

Enterprise AI RAG Platform is a document question-answering application built with FastAPI and PostgreSQL.

It combines retrieval-augmented generation with structured database queries. User questions are processed by an orchestrator that checks for potential prompt injection and routes questions to the appropriate component.

The RAG pipeline retrieves relevant document content, reranks candidate results, constructs context, and uses a local language model to generate a response. Structured questions, such as document counts and file listings, can be handled through the SQL agent.

## Architecture

For the detailed system architecture, ingestion workflow, data layer, and technology decisions, see [Detailed RAG Architecture](architecture/rag_architecture.md).

```mermaid
flowchart TD
    A[User Question] --> B[FastAPI Application]
    B --> C[Security Checks]
    C --> D[Query Orchestrator]
    D -->|Document Question| E[Hybrid Retrieval]
    D -->|Structured Query| F[SQL Agent]
    E --> G[Vector Search and Keyword Search]
    G --> H[Cross-Encoder Reranking]
    H --> I[Relevance Check]
    I --> J[Context Construction]
    J --> K[Local Language Model]
    K --> L[Answer and Source Information]
    F --> M[PostgreSQL]
    M --> N[Structured Result]
```

### Document ingestion

The document ingestion workflow accepts PDF files and optional metadata. The ingestion service processes the file and prepares its content for retrieval.

The retrieval workflow uses:

1. Vector-based semantic retrieval.
2. Keyword-based retrieval.
3. Candidate reranking.
4. Relevance checks.
5. Context construction for answer generation.
6. Source information returned with the answer.

### Structured question answering

The orchestrator can route structured questions to a SQL agent that queries PostgreSQL. This supports questions such as document counts and file listings, depending on the implemented query tools.

### Security checks

The orchestrator checks incoming questions for potential prompt injection before routing them to the RAG or SQL components.

## Key Features

- Document-grounded question answering.
- Hybrid vector and keyword retrieval.
- Reranking of retrieved candidates.
- Metadata filtering by department and document type.
- Source information in RAG responses.
- SQL-based document queries.
- PDF upload and ingestion.
- Prompt-injection detection.
- FastAPI endpoints with interactive documentation.
- Automated API tests using pytest.
- Custom evaluation script with routing, keyword, citation, retrieval, security, and latency checks.
- Docker-based API setup.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API framework | FastAPI |
| Database | PostgreSQL |
| Vector search | pgvector |
| Language models | Hugging Face Transformers |
| Embeddings | Sentence Transformers-compatible embedding models |
| Reranking | Cross-encoder reranker |
| Containerization | Docker |
| Testing | pytest |
| Evaluation | Custom Python evaluation harness |
| Version control | Git and GitHub |

## Project Structure

```text
enterprise-ai-rag-platform/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── ingestion_service.py
│   ├── rag_service.py
│   ├── orchestrator.py
│   └── ...
├── architecture/
├── data/
├── evaluation/
│   ├── test_cases.json
│   └── evaluation_results.json
├── notebooks/
├── scripts/
│   └── run_evaluation.py
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The tree above highlights the main project areas. Additional modules may exist within the application directories.

## Prerequisites

Install the following before running the project:

- Python compatible with the project's dependencies.
- Docker Desktop.
- Git.
- A local PostgreSQL database with the required pgvector extension.
- The project dependencies listed in `requirements.txt`.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/poojapandit1109-boop/enterprise-ai-rag-platform.git
cd enterprise-ai-rag-platform
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use the virtual environment's Python executable directly:

```powershell
venv\Scripts\python.exe --version
```

### 3. Install dependencies

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Update the local configuration using the settings required by your environment. For local Windows execution, the database URL should use `localhost` if PostgreSQL is published on your computer's port 5432.

Example format:

```text
APP_NAME=Enterprise AI RAG Platform
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://ai_user:YOUR_PASSWORD@localhost:5432/enterprise_ai
```

Replace the example username, password, database, and other values with your actual local configuration. Do not commit `.env` or real credentials to GitHub.

The example environment file includes `LLM_API_KEY`, but the current local language model configuration may not require a hosted model API key.

### 5. Start the services

If Docker Desktop is running and the existing Compose configuration is correct for your environment:

```powershell
docker compose up -d
```

Check the running containers:

```powershell
docker ps
```

Ensure PostgreSQL is available and that the API's database configuration is correct before testing database-backed endpoints.

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

When the API is running locally, open:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These interfaces let you inspect the endpoint schemas and submit test requests.

## API Examples

### Health check

**Endpoint:** `GET /health`

```powershell
curl.exe http://localhost:8000/health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Ask a question

**Endpoint:** `POST /ask`

Example request:

```powershell
curl.exe -X POST "http://localhost:8000/ask" `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"What security measures should enterprise AI systems use?\",\"top_k\":3}"
```

The request accepts the following fields:

| Field | Type | Default | Description |
|---|---|---|---|
| `question` | string | Required | Question to process |
| `top_k` | integer | `3` | Number of retrieval candidates requested |
| `department` | string or null | `null` | Optional department filter |
| `document_type` | string or null | `null` | Optional document type filter |

The exact response depends on the selected route and the orchestrator result. Consult the live API documentation for the response schema.

### Upload a PDF

**Endpoint:** `POST /documents/upload`

The endpoint accepts a file and optional `title`, `department`, and `document_type` metadata.

Example PowerShell request:

```powershell
curl.exe -X POST "http://localhost:8000/documents/upload?title=Architecture%20Guide&department=Engineering&document_type=Architecture" -F "file=@C:\path\to\your-document.pdf"
```

Replace `C:\path\to\your-document.pdf` with the full path to a PDF on your computer.

Upload only files you are authorized to process. Authentication and authorization should be added before exposing upload endpoints to untrusted users.

## Testing

Run the API test suite from the project root.

First, configure the database URL in the current PowerShell session for your local PostgreSQL instance:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://ai_user:YOUR_PASSWORD@localhost:5432/enterprise_ai"
```

Replace `YOUR_PASSWORD` with your local development password. Do not share or commit it.

Run the tests:

```powershell
venv\Scripts\python.exe -m pytest -v
```

The current API test suite has passed **7 of 7 tests** in the development environment.

Tests cover the home endpoint, health endpoint, SQL document queries, RAG metadata filtering, unknown questions, and prompt-injection blocking.

Results may differ when the environment, database contents, or model dependencies change.

## Evaluation

Run the evaluation harness from the project root:

```powershell
venv\Scripts\python.exe -m scripts.run_evaluation
```

The current configured evaluation suite contains six cases:

1. Enterprise AI security questions.
2. RAG concepts.
3. Document counts.
4. File listing.
5. Questions whose answers are unavailable.
6. Prompt-injection attempts.

### Latest recorded results

| Metric | Result |
|---|---:|
| Evaluation cases passed | 6 / 6 |
| Configured evaluation pass rate | 100% |
| Route accuracy | 100% |
| Average latency in the recorded run | 0.666 seconds |
| Maximum latency in the recorded run | 2.064 seconds |

These figures describe one recorded run of the current six-case evaluation suite. They are not a guarantee of general answer quality or production performance. Citation and source metrics should be interpreted according to the cases to which those checks apply.

The generated evaluation report is saved to:

```text
evaluation/evaluation_results.json
```

## Security Considerations

The project includes a prompt-injection detection step and basic checks before routing questions to the RAG or SQL components.

Before production deployment, additional safeguards are needed:

- Authentication and role-based authorization.
- Strict database permissions and parameterized query handling.
- File type and file size validation for uploads.
- Protection against unsafe file names and file overwrites.
- Secrets management through environment variables or a dedicated secrets manager.
- Rate limiting and request validation.
- Monitoring, audit logging, and security testing.
- Evaluation against a larger range of prompt-injection and retrieval attacks.

Do not use this development configuration to process confidential documents in a publicly exposed environment without appropriate security controls.

## Limitations and Future Improvements

- Expand the evaluation dataset with realistic and difficult questions.
- Measure retrieval relevance and answer faithfulness.
- Validate citation correctness against source passages.
- Add authentication and authorization for multi-user deployments.
- Improve observability and production deployment configuration.
- Test with a larger and more diverse document collection.
- Add automated continuous integration.
- Establish repeatable performance benchmarks.
- Improve file upload validation and error handling.

## Project Status

This is a portfolio and learning project demonstrating RAG architecture, hybrid retrieval, reranking, local language-model integration, database-backed query routing, evaluation, and basic security checks.

The API tests and configured evaluation cases have passed in the current development environment. The platform is not yet production-ready and requires additional security, reliability, evaluation, and operational work before deployment in a real enterprise environment.

## Author

GitHub: [poojapandit1109-boop](https://github.com/poojapandit1109-boop)

Repository: [Enterprise AI RAG Platform](https://github.com/poojapandit1109-boop/enterprise-ai-rag-platform)