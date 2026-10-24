import asyncio
import logging
import re
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import router
from app.core.config import settings
from app.models.database import AsyncSessionLocal, Base, engine
from app.models.migrations import migrate_legacy_schema
from app.services.ingestion_service import seed_mock_documents
from app.core.exceptions import global_exception_handler
from app.services.retention_service import purge_expired_conversations

logger = logging.getLogger("enterprise_rag")
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
_RATE_WINDOW_SECONDS = 60.0
_RATE_LIMIT_PER_IP = 120
_MAX_REQUEST_BYTES = settings.MAX_UPLOAD_BYTES * 2
_rate_requests: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.APP_ENV.casefold() != "development":
        raise RuntimeError(
            "This local mock build is development-only; production authentication and integrations are not configured."
        )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.run_sync(migrate_legacy_schema)
    async with AsyncSessionLocal() as session:
        await seed_mock_documents(session)
        purged = await purge_expired_conversations(
            session,
            settings.CONVERSATION_RETENTION_DAYS,
        )
        await session.commit()
        if purged:
            logger.info("Purged expired conversations count=%s", purged)
    retention_task = asyncio.create_task(_retention_loop())
    try:
        yield
    finally:
        retention_task.cancel()
        with suppress(asyncio.CancelledError):
            await retention_task
        await engine.dispose()


async def _retention_loop() -> None:
    while True:
        await asyncio.sleep(24 * 60 * 60)
        try:
            async with AsyncSessionLocal() as session:
                purged = await purge_expired_conversations(
                    session,
                    settings.CONVERSATION_RETENTION_DAYS,
                )
                await session.commit()
                if purged:
                    logger.info("Purged expired conversations count=%s", purged)
        except SQLAlchemyError:
            logger.exception("Conversation retention cleanup failed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.exception_handler(Exception)(global_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Mock-Role", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

@app.middleware("http")
async def attach_request_id_and_security_headers(request: Request, call_next):
    supplied_request_id = request.headers.get("X-Request-ID", "")
    request_id = (
        supplied_request_id
        if _REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
        else str(uuid.uuid4())
    )
    request.state.request_id = request_id

    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > _MAX_REQUEST_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body is too large.", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    if request.url.path in {"/api/chat", "/api/documents/upload"}:
        now = time.monotonic()
        client_ip = request.client.host if request.client else "unknown"
        async with _rate_lock:
            if len(_rate_requests) >= 10_000:
                expired = [
                    ip
                    for ip, entries in _rate_requests.items()
                    if not entries or now - entries[-1] > _RATE_WINDOW_SECONDS
                ]
                for ip in expired:
                    _rate_requests.pop(ip, None)
                if client_ip not in _rate_requests and len(_rate_requests) >= 10_000:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many clients. Please try again later."},
                        headers={
                            "Retry-After": str(int(_RATE_WINDOW_SECONDS)),
                            "X-Request-ID": request_id,
                        },
                    )
            requests = _rate_requests[client_ip]
            while requests and now - requests[0] > _RATE_WINDOW_SECONDS:
                requests.popleft()
            if len(requests) >= _RATE_LIMIT_PER_IP:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                    headers={
                        "Retry-After": str(int(_RATE_WINDOW_SECONDS)),
                        "X-Request-ID": request_id,
                    },
                )
            requests.append(now)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Enterprise RAG Platform API", "mode": "local_mock"}