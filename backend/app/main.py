import logging
import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import settings
from app.db.session import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("finpilot")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="FinPilot synthetic wealth operations API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_log(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_failed request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - start) * 1000,
    )
    return response


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("healthcheck_database_failed", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "ok", "service": "finpilot-api", "database": "ok"}


app.include_router(api_router, prefix=settings.api_v1_prefix)
