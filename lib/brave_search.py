import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def search_brave(query, count=20, country="us", search_lang="en"):
    """
    Perform a search using the Brave Search API.

    Args:
        query (str): The search query
        count (int): Number of results to return (default: 20)
        country (str): Country code (default: "us")
        search_lang (str): Language code (default: "en")

    Returns:
        dict: JSON response from the API
    """
    # Get API key from environment variables
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")

    if not api_key:
        raise ValueError("BRAVE_SEARCH_API_KEY not found in environment variables")

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": api_key}
    params = {
        "q": query,
        "count": count,
        "country": country,
        "search_lang": search_lang,
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()
