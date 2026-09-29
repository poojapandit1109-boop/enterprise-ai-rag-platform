from app.sql_agent import run_sql_agent


def main():
    questions = [
        "How many documents are stored?",
        "How many chunks are stored?",
        "Which documents are stored?",
    ]

    for question in questions:
        print("\n==============================")
        print("QUESTION")
        print("==============================")
        print(question)

        result = run_sql_agent(question)

        print("\nSelected Tool:")
        print(result["tool"])

        print("\nResult:")
        print(result["result"])


if __name__ == "__main__":
    main()