from app.sql_service import get_database_summary


def main():
    summary = get_database_summary()

    print("\n==============================")
    print("DATABASE SUMMARY")
    print("==============================")

    print("Total documents:", summary["document_count"])
    print("Total chunks:", summary["chunk_count"])


if __name__ == "__main__":
    main()