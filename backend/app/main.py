"""FastAPI application entrypoint."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.analysis import router as analysis_router
from app.core.config import get_settings
from app.observability.logging import configure_logging

settings = get_settings()
configure_logging()
app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(analysis_router)

_frontend_root = Path("/frontend") if Path("/frontend").exists() else Path(__file__).parents[2] / "frontend"
if _frontend_root.exists():
    app.mount("/assets", StaticFiles(directory=_frontend_root), name="frontend-assets")


@app.get("/", include_in_schema=False)
def demo_home() -> FileResponse:
    candidates = (
        Path("/frontend/index.html"),
        Path(__file__).parents[2] / "frontend" / "index.html",
    )
    for candidate in candidates:
        if candidate.exists():
            return FileResponse(candidate)
    raise FileNotFoundError("frontend/index.html is not available")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Report process health without asserting database readiness."""

    return {"status": "ok"}
