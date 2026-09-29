from app.query_router import route_query


def main():
    questions = [
        "How many documents are stored?",
        "Which documents are stored?",
        "What security measures should enterprise AI systems use?",
        "How does the system retrieve information?",
    ]

    for question in questions:
        route = route_query(question)

        print("\n==============================")
        print("QUESTION")
        print("==============================")
        print(question)

        print("\nROUTE:")
        print(route)


if __name__ == "__main__":
    main()