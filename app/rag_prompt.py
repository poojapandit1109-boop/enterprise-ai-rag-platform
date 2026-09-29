def build_rag_prompt(
    question: str,
    context: str,
) -> str:
    return f"""
You are an enterprise AI assistant.

Answer the user's question using ONLY the provided context.

Instructions:
- Give a complete and direct answer.
- Use simple, professional language.
- Do not invent information.
- If the answer is not present in the context, say:
  "The information was not found in the provided documents."
- Do not repeat the question.
- Do not add information from your own knowledge.
- At the end of each factual statement, include the relevant citation.
- Use citations exactly in this format: [Source 1], [Source 2].
- Only use source numbers that exist in the provided context.

Context:
{context}

User Question:
{question}

Answer:
""".strip()