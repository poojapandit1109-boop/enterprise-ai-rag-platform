
# Enterprise AI RAG Platform — Architecture

## 1. System Architecture

```mermaid
flowchart TB
    USER["User / Client"]
    API["FastAPI Application"]
    
    subgraph INGEST["Document Ingestion Pipeline"]
        UPLOAD["PDF Upload API"]
        PARSE["PDF Text Extraction"]
        CHUNK["Text Chunking"]
        EMBED["Sentence Transformer<br/>all-MiniLM-L6-v2"]
        STORE["Store Chunks and Embeddings"]
    end

    subgraph DATA["Data Layer"]
        DB[("PostgreSQL + pgvector")]
        META["Document Metadata"]
        VECTORS["Vector Embeddings"]
    end

    subgraph RETRIEVAL["Retrieval and Generation"]
        ROUTER["Query Router"]
        SECURITY["Prompt Injection Detection"]
        HYBRID["Hybrid Search"]
        RERANK["Cross-Encoder Reranking"]
        CONTEXT["Context Assembly"]
        LLM["Local LLM<br/>Flan-T5 Small"]
        CITATIONS["Source Citations"]
    end

    USER --> API
    API --> UPLOAD
    UPLOAD --> PARSE
    PARSE --> CHUNK
    CHUNK --> EMBED
    EMBED --> STORE
    STORE --> DB
    DB --- META
    DB --- VECTORS

    API --> SECURITY
    SECURITY --> ROUTER
    ROUTER -->|Knowledge question| HYBRID
    ROUTER -->|Database question| DB
    HYBRID --> DB
    HYBRID --> RERANK
    RERANK --> CONTEXT
    CONTEXT --> LLM
    LLM --> CITATIONS
    CITATIONS --> API
    DB --> API
    API --> USER
```

## 2. Request Flow

1. A user submits a question through the API.
2. The security layer checks for prompt injection.
3. The query router chooses the appropriate processing path.
4. Knowledge questions use hybrid retrieval against PostgreSQL and pgvector.
5. Retrieved chunks are reranked and assembled into context.
6. The local language model generates a response using the retrieved context.
7. The response includes source citations where applicable.
8. Database questions follow the SQL processing path.

## 3. Document Ingestion Flow

1. The user uploads a PDF through the document upload endpoint.
2. The application extracts text from the PDF.
3. Extracted text is divided into smaller chunks.
4. The embedding model converts the chunks into vector representations.
5. The chunks, vectors, and associated metadata are stored in PostgreSQL with pgvector.

## 4. Technology Stack

| Component | Technology |
|---|---|
| API | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| Vector Search | pgvector |
| Embeddings | sentence-transformers / all-MiniLM-L6-v2 |
| Reranking | Cross-Encoder |
| Local Language Model | google/flan-t5-small |
| Containerization | Docker |
| Testing | pytest |

## 5. Important API Endpoints

- `GET /` — API welcome response
- `GET /health` — Health check
- `POST /ask` — Ask a question
- `POST /documents/upload` — Upload a document

## 6. Design Notes

- Document ingestion and question answering are separate flows.
- PostgreSQL stores document information and vector embeddings.
- Hybrid retrieval combines multiple retrieval signals before reranking.
- The query router supports both knowledge retrieval and database questions.
- The application includes prompt-injection checks and automated evaluation.

> Note: This diagram represents the intended high-level flow of the implemented project. Verify exact internal function names and routing behavior against the current source code before using it as a production deployment specification.
