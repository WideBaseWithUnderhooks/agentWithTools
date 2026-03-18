from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """
    Search the web for real-time information.
    Use this for news, current events, or facts not in your training data.
    """
    # TODO: Change this to Tavily or Serper.
    search = DuckDuckGoSearchRun()
    return search.run(query)