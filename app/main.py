from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI RAG Platform",
    description="Enterprise RAG and AI Agent Platform",
    version="1.0.0",
)


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