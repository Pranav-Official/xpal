from fastapi import APIRouter, Query, HTTPException
from app.research_agent import start_research_workflow
import traceback

router = APIRouter(prefix="/api/articles")


@router.get("/")
async def get_articles(
    query: str = Query(..., min_length=1), count: int = Query(20, ge=1, le=100), instructions: str = Query('', min_length=0, max_length=1000)
):
    """
    Search for articles based on a query string.

    - **query**: The search query (required)
    - **count**: Number of results to return (default: 20, min: 1, max: 100)
    """
    try:
        results = start_research_workflow(query, count, instructions)
        return results
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error searching articles: {str(e)}"
        )
