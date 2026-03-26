from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool
def web_search(query) -> str:
    """Search the web for a query string and return results."""
    if isinstance(query, dict) and "value" in query:
        query = query["value"]
    if not isinstance(query, str):
        raise ValueError("query must be string")
    print("web_search CALLED with:", repr(query))
    search = DuckDuckGoSearchRun()
    result = search.run(query)
    print("web_search RESULT:", repr(result))
    return result