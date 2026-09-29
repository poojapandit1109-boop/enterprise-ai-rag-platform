from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


MODEL_NAME = "google/flan-t5-small"


def main():
    print("Loading local LLM...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    prompt = """
Answer the question using the information provided.

Context:
Retrieval-Augmented Generation retrieves relevant information
from stored documents and provides it to a language model as context.

Question:
How does RAG retrieve information?
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
    )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    print("\nGenerated answer:")
    print(answer)


if __name__ == "__main__":
    main()