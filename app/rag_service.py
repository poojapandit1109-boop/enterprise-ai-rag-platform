from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.context_builder import build_context
from app.rag_prompt import build_rag_prompt
from app.hybrid_search import hybrid_search
from app.reranker import rerank_results


MODEL_NAME = "google/flan-t5-small"

# Maximum vector distance considered relevant.
RELEVANCE_THRESHOLD = 0.80

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generate_answer(
    question: str,
    top_k: int = 3,
) -> dict:
    # --------------------------------------------------
    # Step 1: Hybrid retrieval
    # --------------------------------------------------

    retrieval_results = hybrid_search(
        question,
        top_k=5,
    )

    if not retrieval_results:
        return {
            "question": question,
            "answer": (
                "The information was not found "
                "in the provided documents."
            ),
            "sources": [],
        }

    # --------------------------------------------------
    # Step 2: Rerank retrieved candidates
    # --------------------------------------------------

    results = rerank_results(
        query=question,
        results=retrieval_results,
        top_k=top_k,
    )

    if not results:
        return {
            "question": question,
            "answer": (
                "The information was not found "
                "in the provided documents."
            ),
            "sources": [],
        }

    # --------------------------------------------------
    # Step 3: Relevance check
    # --------------------------------------------------

    best_result = results[0]

    vector_distance = best_result.get(
        "vector_distance"
    )

    keyword_match = best_result.get(
        "keyword_match",
        False,
    )

    vector_is_relevant = (
        vector_distance is not None
        and vector_distance <= RELEVANCE_THRESHOLD
    )

    if not vector_is_relevant and not keyword_match:
        return {
            "question": question,
            "answer": (
                "The information was not found "
                "in the provided documents."
            ),
            "sources": [],
        }

    # --------------------------------------------------
    # Step 4: Build context from reranked results
    # --------------------------------------------------

    context = build_context(results)

    # --------------------------------------------------
    # Step 5: Build RAG prompt
    # --------------------------------------------------

    prompt = build_rag_prompt(
        question,
        context,
    )

    # --------------------------------------------------
    # Step 6: Generate answer
    # --------------------------------------------------

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        do_sample=False,
    )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    ).strip()

    # --------------------------------------------------
    # Step 7: Add deterministic citation
    # --------------------------------------------------

    if results and "[Source" not in answer:
        answer = f"{answer} [Source 1]"

    # --------------------------------------------------
    # Step 8: Build structured sources
    # --------------------------------------------------

    sources = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        sources.append(
            {
                "source": f"Source {index}",
                "document_id": result["document_id"],
                "filename": result["filename"],
                "title": result["title"],
                "chunk_index": result["chunk_index"],
                "fusion_score": result.get(
                    "fusion_score",
                    0.0,
                ),
                "reranker_score": result.get(
                    "reranker_score"
                ),
                "vector_distance": result.get(
                    "vector_distance"
                ),
                "keyword_match": result.get(
                    "keyword_match",
                    False,
                ),
                "content": result["content"],
            }
        )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }