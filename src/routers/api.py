"""API router for the GitIngest service."""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from query_processor import process_api_query
from server_utils import limiter

router = APIRouter()

@router.get("/ingest")
@limiter.limit("10/minute")
async def ingest_url(
    request: Request,
    url: str = Query(..., description="The URL of the Git repository to ingest"),
    max_file_size: int = Query(243, description="Maximum file size to include (0-500)"),
    pattern_type: str = Query("exclude", description="Pattern type: 'include' or 'exclude'"),
    pattern: str = Query("", description="Pattern to include or exclude files"),
) -> JSONResponse:
    """Ingest a Git repository from a URL and return its contents."""
    try:
        result = await process_api_query(
            input_text=url,
            max_file_size=max_file_size,
            pattern_type=pattern_type,
            pattern=pattern,
        )

        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={"error": result["error"]},
            )

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e