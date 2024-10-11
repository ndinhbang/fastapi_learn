from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from rich.console import Console
from rich.traceback import install

from app.settings import settings
from app.database import session_manager

# Install rich traceback
install(show_locals=True)

# Create a console to print traceback
console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if session_manager._engine is not None:
        # Close the DB connection
        await session_manager.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    version="0.0.1",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Print traceback to console
    console.print_exception(show_locals=True)
    # Return error response
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}
