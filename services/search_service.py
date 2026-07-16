import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def search_web(query: str, max_results: int = 5):
    """
    Search the web using Tavily.

    Parameters
    ----------
    query : str
        User research topic.

    max_results : int
        Number of web sources to retrieve.
        Quick    -> 3
        Standard -> 5
        Deep     -> 10
    """

    try:

        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )

        results = []
        sources = []

        for item in response.get("results", []):

            content = item.get("content", "")
            url = item.get("url", "")

            if content:
                results.append(content)

            if url:
                sources.append(url)

        return {
            "raw_results": "\n\n".join(results),
            "sources": sources,
            "total_sources": len(sources)
        }

    except Exception as e:

        return {
            "error": str(e),
            "raw_results": "",
            "sources": [],
            "total_sources": 0
        }