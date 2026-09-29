from app.sql_tools import execute_sql_tool


def main():
    print("\n==============================")
    print("SQL TOOL RESULT")
    print("==============================")

    summary = execute_sql_tool("database_summary")

    print("Documents:", summary["document_count"])
    print("Chunks:", summary["chunk_count"])

    print("\n==============================")
    print("DOCUMENT LIST")
    print("==============================")

    documents = execute_sql_tool("list_documents")

    for document in documents:
        print("\nDocument ID:", document["id"])
        print("Filename:", document["filename"])
        print("Title:", document["title"])
        print("Uploaded:", document["uploaded_at"])


if __name__ == "__main__":
    main()