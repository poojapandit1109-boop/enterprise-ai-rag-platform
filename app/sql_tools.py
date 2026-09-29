from app.sql_service import (
    get_database_summary,
    get_documents,
)


def execute_sql_tool(tool_name: str) -> dict | list:
    """
    Execute a safe, predefined SQL tool.
    """

    if tool_name == "database_summary":
        return get_database_summary()

    if tool_name == "list_documents":
        return get_documents()

    return {
        "error": f"Unknown SQL tool: {tool_name}"
    }