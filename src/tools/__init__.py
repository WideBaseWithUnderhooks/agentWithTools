from .web_search import web_search

# The single source of truth for the agent's capabilities
TOOLS = [
    web_search,
]

__all__ = [
    "web_search",
    "TOOLS",
]