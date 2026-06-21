from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.schemas import ErrorResponse, ProductsPage
from app.service import list_products

app = FastAPI(title="CodeVector Products API", version="0.1.0")
static_root = Path(__file__).with_name("static")

app.mount("/static", StaticFiles(directory=static_root), name="static")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "codevector-products-api"}


@app.get("/browse")
def browse() -> FileResponse:
    return FileResponse(static_root / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/products", response_model=ProductsPage, responses={400: {"model": ErrorResponse}})
def get_products(
    category: str | None = None,
    cursor: str | None = None,
    limit: int = Query(default=settings.default_page_size, ge=1, le=settings.max_page_size),
    session: Session = Depends(get_db),
) -> ProductsPage:
    try:
        return list_products(session=session, category=category, cursor=cursor, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
