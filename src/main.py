"""Main module for the FastAPI application."""

import asyncio
import shutil
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import DELETE_REPO_AFTER, TMP_BASE_PATH
from routers import api
from server_utils import limiter

async def remove_old_repositories():
    """Background task that runs periodically to clean up old repository directories."""
    while True:
        try:
            if not TMP_BASE_PATH.exists():
                await asyncio.sleep(60)
                continue

            current_time = time.time()

            for folder in TMP_BASE_PATH.iterdir():
                if not folder.is_dir():
                    continue

                if current_time - folder.stat().st_ctime <= DELETE_REPO_AFTER:
                    continue

                try:
                    shutil.rmtree(folder)
                except Exception as e:
                    print(f"Error deleting {folder}: {e}")

        except Exception as e:
            print(f"Error in remove_old_repositories: {e}")

        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    task = asyncio.create_task(remove_old_repositories())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# Initialize the FastAPI application
app = FastAPI(
    title="GitIngest API",
    description="Headless API for ingesting GitHub repositories",
    version="1.0.0",
    lifespan=lifespan
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, 
    lambda req, exc: _rate_limit_exceeded_handler(req, exc)
)

# Include only the API router
app.include_router(api, prefix="/api/v1", tags=["api"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
