from typing import List, Optional
from pydantic import BaseModel
from lib.brave_search import search_brave


class SearchResultItem(BaseModel):
    """Model for a single search result item"""

    title: str
    url: str
    description: str


class SearchResponse(BaseModel):
    """Model for the search response"""

    results: List[SearchResultItem]


def search_articles(query: str, count: int = 20) -> List[SearchResultItem]:
    """
    Search for articles using Brave Search API and return a formatted list of results.

    Args:
        query (str): The search query
        count (int): Number of results to return (default: 20)

    Returns:
        List[SearchResultItem]: A list of search result items containing title, url, and description
    """
    try:
        # Perform the search using the Brave Search API
        response = search_brave(query, count=count)

        # Extract the web results
        web_results = response.get("web", {}).get("results", [])

        # Format the results
        formatted_results: List[SearchResultItem] = []
        for result in web_results:
            # Only include results that have the required fields
            if "title" in result and "url" in result and "description" in result:
                formatted_results.append(
                    SearchResultItem(
                        title=result["title"],
                        url=result["url"],
                        description=result["description"],
                    )
                )

        return formatted_results
    except Exception as e:
        print(f"Error searching articles: {e}")
        return []
