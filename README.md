# Enterprise AI RAG Platform

An enterprise-oriented Retrieval-Augmented Generation (RAG) platform that combines semantic search, keyword retrieval, reranking, a local language model, SQL-based document queries, and prompt-injection protection.

## Overview

This project demonstrates how to build a document question-answering system that retrieves relevant information from a knowledge base and generates answers grounded in retrieved content.

It also routes structured data questions to a SQL agent and blocks requests identified as potential prompt-injection attempts.

## Architecture

```text
                  User Question
                        |
                        v
                 FastAPI Application
                        |
                        v
                Security / Guardrails
                        |
                        v
                   Query Router
                   /          \
                  /            \
             RAG Route        SQL Route
                 |                |
                 v                v
          Hybrid Retrieval     SQL Agent
          (Vector + Keyword)      |
                 |                v
                 v             PostgreSQL
              Reranker
                 |
                 v
          Context Construction
                 |
                 v
          Local Language Model
                 |
                 v
        Answer + Source Citations
```

### Document ingestion and retrieval

The document pipeline prepares document content for retrieval, generates embeddings, and stores searchable information in PostgreSQL with pgvector.

At query time, the RAG pipeline:

1. Retrieves candidate content using hybrid search.
2. Reranks retrieved results.
3. Checks whether the best result meets the relevance criteria.
4. Builds context for the language model.
5. Generates an answer and returns structured source information.

### SQL question answering

Structured questions, such as document counts and file listings, are routed to a SQL agent that queries PostgreSQL.

### Security

The orchestrator checks incoming questions for potential prompt injection before routing them to the RAG or SQL components.

## Technology Stack

- **Language:** Python
- **API:** FastAPI
- **Database:** PostgreSQL
- **Vector search:** pgvector
- **Language models:** Hugging Face Transformers
- **Embeddings and reranking:** Local embedding and reranker models
- **Containerization:** Docker
- **Testing:** Pytest
- **Evaluation:** Custom RAG evaluation script

## Key Features

- Document-grounded question answering
- Hybrid retrieval and reranking
- Metadata filtering by department and document type
- Structured source citations
- SQL-based document queries
- Prompt-injection detection
- Automated API tests
- Evaluation reports with route, keyword, citation, retrieval, security, and latency checks

## Evaluation

The current evaluation suite contains six test cases covering:

- Enterprise AI security questions
- RAG concepts
- Document counts
- File listing
- Questions for which the answer is not available
- Prompt-injection attempts

**Latest reported result:** 6 of 6 evaluation cases passed (100%).

The score reflects the current test suite's routing and configured checks. It does not establish perfect factual accuracy or production readiness.

## Running the Project

### Prerequisites

- Python
- Docker Desktop
- Git

### Start the API

Start the configured Docker services using the project's existing Compose configuration:

```powershell
docker compose up -d
```

Check the API health endpoint:

```powershell
curl.exe http://localhost:8000/health
```

Expected response:

```json
{"status":"healthy"}
```

### Run automated tests

```powershell
venv\Scripts\python.exe -m pytest tests\test_api.py -v
```

### Run the evaluation suite

For local Python execution on Windows, set the database URL for the current PowerShell session to your local PostgreSQL connection:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://ai_user:YOUR_PASSWORD@localhost:5432/enterprise_ai"
venv\Scripts\python.exe -m scripts.run_evaluation
```

Replace `YOUR_PASSWORD` with your actual local development password. Never commit real credentials to GitHub.

## API Examples

### Health check

```http
GET /health
```

### Ask a question

The exact request schema depends on the API endpoint implementation. Inspect the FastAPI documentation at:

http://localhost:8000/docs

Use that interactive documentation to submit a question and inspect the returned answer and sources.

## Limitations and Future Improvements

- Expand the evaluation dataset with more realistic questions and difficult retrieval cases.
- Evaluate answer faithfulness, retrieval relevance, and citation correctness.
- Add authentication and authorization for multi-user deployments.
- Improve observability and production deployment configuration.
- Test behavior on a larger and more diverse document collection.

## Project Status

This is a portfolio and learning project demonstrating RAG architecture, retrieval, routing, database integration, evaluation, and basic security controls. It should not be considered production-ready without additional testing and operational safeguards.
