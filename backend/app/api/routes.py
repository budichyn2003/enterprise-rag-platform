import base64
import binascii
import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import (
    AsyncSessionLocal,
    AuditLog,
    BotConfiguration,
    ChatFeedback,
    Conversation,
    DocumentChunk,
    DocumentRecord,
    DocumentVersion,
    HandoffTicket,
    Message,
)
from app.models.schemas import (
    BotConfigurationRequest,
    ChatRequest,
    ChatResponse,
    DocumentMetadata,
    DocumentUpdateRequest,
    DocumentUploadRequest,
    DocumentUploadResponse,
    FeedbackRequest,
    HandoffRequest,
)
from app.services.guardrails import redact_pii
from app.services.ingestion_service import (
    extract_document_text,
    index_document,
)
from app.services.mock_data import MOCK_CONNECTORS
from app.services.rag_service import rag_service

router = APIRouter()
_VALID_ROLES = {"admin", "knowledge_manager", "agent", "viewer"}
_ROLE_ACCESS = {
    "admin": _VALID_ROLES,
    "knowledge_manager": {"knowledge_manager", "viewer"},
    "agent": {"agent", "viewer"},
    "viewer": {"viewer"},
}


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def require_roles(*allowed_roles: str):
    async def role_guard(
        x_mock_role: str | None = Header(default=None, alias="X-Mock-Role"),
    ) -> str:
        if settings.APP_ENV.casefold() != "development" or not settings.MOCK_AUTH_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="Demo authentication is disabled outside development mode.",
            )
        if x_mock_role not in _VALID_ROLES:
            raise HTTPException(status_code=401, detail="Internal demo role is required.")
        if not _ROLE_ACCESS[x_mock_role].intersection(allowed_roles):
            raise HTTPException(status_code=403, detail="Role is not permitted for this action.")
        return x_mock_role

    return role_guard


async def _audit(
    session: AsyncSession,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    session.add(
        AuditLog(
            actor_role=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
    )


def _public_document(document: DocumentRecord) -> dict[str, Any]:
    metadata = document.metadata_info or {}
    return {
        "id": document.id,
        "title": document.title,
        "source_type": document.source_type,
        "status": document.status,
        "category": metadata.get("category", "general"),
        "language": metadata.get("language", "id"),
        "product": metadata.get("product", "general"),
        "region": metadata.get("region", "global"),
        "sensitivity": metadata.get("sensitivity", "public"),
        "source_url": metadata.get("source_url"),
        "created_at": document.created_at,
        "updated_at": document.updated_at,
    }


def _metadata_dict(metadata: DocumentMetadata) -> dict[str, Any]:
    return metadata.model_dump(mode="json")


async def _create_handoff(
    session: AsyncSession,
    conversation_id: str,
    reason: str,
) -> HandoffTicket:
    messages = (
        await session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(100)
        )
    ).all()
    customer_messages = [message.content for message in messages if message.role == "user"]
    summary = redact_pii(" | ".join(customer_messages[-3:])[:1_000])
    ticket = HandoffTicket(
        conversation_id=conversation_id,
        reason=reason,
        summary=summary or "Pelanggan meminta bantuan agent.",
        context=[
            {
                "role": message.role,
                "content": redact_pii(message.content),
                "citations": message.citations or [],
            }
            for message in messages
        ],
    )
    session.add(ticket)
    return ticket


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, session: AsyncSession = Depends(get_db)):
    session_id = request.session_id
    if session_id:
        try:
            uuid.UUID(session_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Session ID tidak valid.") from exc
        conversation = await session.get(Conversation, session_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Sesi percakapan tidak ditemukan.")
    else:
        session_id = str(uuid.uuid4())
        conversation = Conversation(id=session_id, language=request.language)
        session.add(conversation)
        await session.flush()
    if conversation.containment_status == "resolved":
        conversation.containment_status = "active"

    previous_messages = (
        await session.scalars(
            select(Message)
            .where(Message.conversation_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(12)
        )
    ).all()
    history = [
        {"role": message.role, "content": message.content}
        for message in reversed(previous_messages)
    ]
    safe_message = redact_pii(request.message)
    session.add(
        Message(
            conversation_id=session_id,
            role="user",
            content=safe_message,
        )
    )
    effective_request = request.model_copy(
        update={"session_id": session_id, "message": safe_message}
    )
    bot_config = await session.get(BotConfiguration, 1)
    config = bot_config.settings if bot_config else {}
    response = await rag_service.generate_response(
        session,
        effective_request,
        history,
        confidence_threshold=config.get("confidence_threshold", 0.35),
        max_context_chunks=config.get("max_context_chunks", 4),
        allowed_topics=config.get(
            "allowed_topics",
            ["returns", "shipping", "support", "accounts", "billing"],
        ),
    )
    assistant_message = Message(
        conversation_id=session_id,
        role="ai",
        content=redact_pii(response.answer),
        confidence_score=response.confidence_score,
        citations=[citation.model_dump(mode="json") for citation in response.citations],
        needs_escalation=response.needs_escalation,
    )
    session.add(assistant_message)
    await session.flush()
    response.message_id = assistant_message.id

    if response.needs_escalation:
        conversation.containment_status = "escalated"
        handoff = await _create_handoff(
            session,
            session_id,
            "prompt_guardrail_or_low_confidence",
        )
        await session.flush()
        response.handoff_id = handoff.id
    conversation.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return response


@router.post("/chat/{session_id}/feedback")
async def submit_feedback(
    session_id: str,
    payload: FeedbackRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        uuid.UUID(session_id)
        uuid.UUID(payload.message_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="ID percakapan tidak valid.") from exc
    conversation = await session.get(Conversation, session_id)
    message = await session.get(Message, payload.message_id)
    if conversation is None or message is None or message.conversation_id != session_id:
        raise HTTPException(status_code=404, detail="Jawaban tidak ditemukan.")
    if message.role != "ai":
        raise HTTPException(status_code=422, detail="Feedback hanya berlaku untuk jawaban bot.")
    existing = await session.scalar(
        select(ChatFeedback).where(ChatFeedback.message_id == payload.message_id)
    )
    if existing:
        existing.rating = payload.rating
        existing.comment = redact_pii(payload.comment or "") or None
    else:
        session.add(
            ChatFeedback(
                conversation_id=session_id,
                message_id=payload.message_id,
                rating=payload.rating,
                comment=redact_pii(payload.comment or "") or None,
            )
        )
    await session.commit()
    return {"status": "recorded"}


@router.post("/chat/{session_id}/handoff")
async def request_handoff(
    session_id: str,
    payload: HandoffRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        uuid.UUID(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Session ID tidak valid.") from exc
    conversation = await session.get(Conversation, session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Sesi percakapan tidak ditemukan.")
    ticket = await _create_handoff(session, session_id, payload.reason)
    conversation.containment_status = "escalated"
    await session.commit()
    return {
        "handoff_id": ticket.id,
        "status": ticket.status,
        "estimated_wait_minutes": 5,
        "message": "Permintaan diteruskan ke agent demo.",
    }


@router.post("/chat/{session_id}/resolve")
async def resolve_conversation(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
    try:
        uuid.UUID(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Session ID tidak valid.") from exc
    conversation = await session.get(Conversation, session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Sesi percakapan tidak ditemukan.")
    if conversation.containment_status != "escalated":
        conversation.containment_status = "resolved"
    conversation.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"status": conversation.containment_status}


@router.delete("/chat/{session_id}")
async def delete_conversation_data(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
    try:
        uuid.UUID(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Session ID tidak valid.") from exc
    conversation = await session.get(Conversation, session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Sesi percakapan tidak ditemukan.")
    await session.execute(
        delete(ChatFeedback).where(ChatFeedback.conversation_id == session_id)
    )
    await session.execute(
        delete(HandoffTicket).where(HandoffTicket.conversation_id == session_id)
    )
    await session.execute(delete(Message).where(Message.conversation_id == session_id))
    await session.delete(conversation)
    session.add(
        AuditLog(
            actor_role="customer",
            action="conversation.delete",
            resource_type="conversation",
        )
    )
    await session.commit()
    return {"status": "deleted"}


@router.get("/documents")
async def list_documents(
    status: str | None = Query(default=None, max_length=20),
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "viewer", "agent")),
):
    query = select(DocumentRecord).order_by(DocumentRecord.updated_at.desc())
    if status:
        query = query.where(DocumentRecord.status == status)
    documents = list((await session.scalars(query)).all())
    if q:
        needle = q.casefold()
        documents = [
            document
            for document in documents
            if needle in document.title.casefold()
            or needle in str(document.metadata_info or {}).casefold()
        ]
    total = len(documents)
    return {
        "items": [_public_document(document) for document in documents[offset : offset + limit]],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    payload: DocumentUploadRequest,
    session: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles("admin", "knowledge_manager")),
):
    try:
        raw = base64.b64decode(payload.content_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Konten file tidak valid.") from exc
    if len(raw) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi batas.")
    try:
        content = extract_document_text(payload.filename, raw)
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    safe_title = payload.filename.replace("\\", "/").rsplit("/", 1)[-1]
    metadata = _metadata_dict(payload.metadata)
    document, chunks_processed = await index_document(
        session,
        title=safe_title,
        content=content,
        metadata=metadata,
    )
    await _audit(
        session,
        role,
        "document.upload",
        "document",
        document.id,
        {"chunk_count": chunks_processed, "source_type": metadata["source_type"]},
    )
    await session.commit()
    return DocumentUploadResponse(
        document_id=document.id,
        status="indexed",
        chunks_processed=chunks_processed,
        message="Dokumen mock berhasil diproses dan dapat diuji melalui chat.",
    )


@router.patch("/documents/{document_id}")
async def update_document(
    document_id: str,
    payload: DocumentUpdateRequest,
    session: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles("admin", "knowledge_manager")),
):
    document = await session.get(DocumentRecord, document_id)
    if document is None or document.status == "deleted":
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan.")
    current_version = await session.scalar(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version.desc())
        .limit(1)
    )
    if current_version is None:
        raise HTTPException(status_code=409, detail="Versi dokumen aktif tidak ditemukan.")
    metadata = _metadata_dict(payload.metadata) if payload.metadata else document.metadata_info or {}
    title = payload.title or document.title
    await index_document(
        session,
        title=title,
        content=current_version.content,
        metadata=metadata,
        document_id=document_id,
    )
    await _audit(session, role, "document.update", "document", document_id)
    await session.commit()
    return _public_document(document)


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    session: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles("admin", "knowledge_manager")),
):
    document = await session.get(DocumentRecord, document_id)
    if document is None or document.status == "deleted":
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan.")
    await session.execute(
        DocumentChunk.__table__.delete().where(DocumentChunk.document_id == document_id)
    )
    document.status = "deleted"
    await _audit(session, role, "document.delete", "document", document_id)
    await session.commit()
    return {"status": "deleted", "document_id": document_id}


@router.post("/documents/{document_id}/rollback/{version}")
async def rollback_document(
    document_id: str,
    version: int,
    session: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles("admin", "knowledge_manager")),
):
    previous = await session.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version == version,
        )
    )
    document = await session.get(DocumentRecord, document_id)
    if previous is None or document is None:
        raise HTTPException(status_code=404, detail="Versi dokumen tidak ditemukan.")
    metadata = previous.metadata_info or document.metadata_info or {}
    await index_document(
        session,
        title=previous.title,
        content=previous.content,
        metadata=metadata,
        document_id=document_id,
    )
    await _audit(
        session,
        role,
        "document.rollback",
        "document",
        document_id,
        {"restored_version": version},
    )
    await session.commit()
    return _public_document(document)


@router.post("/documents/sync/{connector}")
async def sync_mock_connector(
    connector: str,
    session: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles("admin", "knowledge_manager")),
):
    fixtures = MOCK_CONNECTORS.get(connector)
    if fixtures is None:
        raise HTTPException(status_code=404, detail="Konektor demo tidak dikenal.")
    created: list[str] = []
    for fixture in fixtures:
        existing = await session.scalar(
            select(DocumentRecord).where(
                DocumentRecord.title == fixture["title"],
                DocumentRecord.source_type == fixture["source_type"],
                DocumentRecord.status == "indexed",
            )
        )
        if existing:
            continue
        metadata = {
            "source_type": fixture["source_type"],
            "category": fixture["category"],
            "language": fixture["language"],
            "product": "general",
            "region": "global",
            "sensitivity": "public",
            "source_url": f"https://example.invalid/mock/{connector}/{fixture['title'].lower().replace(' ', '-')}",
        }
        document, _ = await index_document(
            session,
            title=fixture["title"],
            content=redact_pii(fixture["content"]),
            metadata=metadata,
        )
        created.append(document.id)
    await _audit(
        session,
        role,
        "connector.sync",
        "connector",
        connector,
        {"documents_created": len(created), "mode": "mock"},
    )
    await session.commit()
    return {"connector": connector, "mode": "mock", "documents_created": created}


@router.get("/documents/{document_id}/versions")
async def list_document_versions(
    document_id: str,
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "viewer")),
):
    versions = (
        await session.scalars(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
        )
    ).all()
    if not versions:
        raise HTTPException(status_code=404, detail="Versi dokumen tidak ditemukan.")
    return [
        {
            "version": version.version,
            "title": version.title,
            "created_at": version.created_at,
        }
        for version in versions
    ]


@router.get("/documents/{document_id}/test")
async def test_document_query(
    document_id: str,
    q: str = Query(min_length=2, max_length=300),
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager")),
):
    document = await session.get(DocumentRecord, document_id)
    if document is None or document.status != "indexed":
        raise HTTPException(status_code=404, detail="Dokumen terindeks tidak ditemukan.")
    results = await rag_service.retrieve_documents(
        session,
        q,
        language=(document.metadata_info or {}).get("language", "id"),
        product=(document.metadata_info or {}).get("product"),
        region=(document.metadata_info or {}).get("region"),
        allowed_topics=None,
    )
    return {
        "query": q,
        "results": [item for item in results if item["document_id"] == document_id],
    }


@router.get("/analytics/overview")
async def analytics_overview(
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "agent", "viewer")),
):
    total_conversations = await session.scalar(select(func.count()).select_from(Conversation)) or 0
    escalated = await session.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.containment_status == "escalated")
    ) or 0
    resolved = await session.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.containment_status == "resolved")
    ) or 0
    feedback = await session.scalar(select(func.avg(ChatFeedback.rating))) or 0
    total_documents = await session.scalar(
        select(func.count()).select_from(DocumentRecord).where(DocumentRecord.status == "indexed")
    ) or 0
    total_messages = await session.scalar(select(func.count()).select_from(Message)) or 0
    completed_times = (
        await session.execute(
            select(Conversation.created_at, Conversation.updated_at)
            .where(Conversation.containment_status != "active")
        )
    ).all()
    average_handling_seconds = (
        sum(max(0.0, (updated - created).total_seconds()) for created, updated in completed_times)
        / len(completed_times)
        if completed_times
        else 0.0
    )
    status_counts = (
        await session.execute(
            select(Conversation.containment_status, func.count())
            .group_by(Conversation.containment_status)
        )
    ).all()
    return {
        "conversations": total_conversations,
        "containment_rate": round(resolved / (resolved + escalated), 4)
        if resolved + escalated
        else 0,
        "resolved_conversations": resolved,
        "escalated_conversations": escalated,
        "average_csat": round(float(feedback), 2),
        "average_handling_time_seconds": round(average_handling_seconds, 2),
        "indexed_documents": total_documents,
        "messages": total_messages,
        "conversation_status": {status: count for status, count in status_counts},
        "mode": "local_mock",
    }


@router.get("/analytics/knowledge-gaps")
async def knowledge_gaps(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "agent", "viewer")),
):
    escalated_user_messages = (
        await session.execute(
            select(Message.content, func.count(Message.id).label("occurrences"))
            .join(Conversation, Conversation.id == Message.conversation_id)
            .where(
                Conversation.containment_status == "escalated",
                Message.role == "user",
            )
            .group_by(Message.content)
            .order_by(func.count(Message.id).desc())
            .limit(limit)
        )
    ).all()
    return [
        {"question": redact_pii(content), "occurrences": occurrences}
        for content, occurrences in escalated_user_messages
    ]


@router.get("/analytics/conversations")
async def search_conversations(
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "agent", "viewer")),
):
    conversations = list(
        (
            await session.scalars(
                select(Conversation)
                .order_by(Conversation.updated_at.desc())
                .limit(1_000)
            )
        ).all()
    )
    results: list[dict[str, Any]] = []
    for conversation in conversations:
        messages = (
            await session.scalars(
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.asc())
                .limit(100)
            )
        ).all()
        transcript = " ".join(message.content for message in messages)
        if q and q.casefold() not in transcript.casefold():
            continue
        results.append(
            {
                "session_id": conversation.id,
                "status": conversation.containment_status,
                "language": conversation.language,
                "updated_at": conversation.updated_at,
                "messages": [
                    {
                        "id": message.id,
                        "role": message.role,
                        "content": message.content,
                        "confidence_score": message.confidence_score,
                        "citations": message.citations or [],
                        "needs_escalation": message.needs_escalation,
                        "created_at": message.created_at,
                    }
                    for message in messages
                ],
            }
        )
    return {"items": results[offset : offset + limit], "total": len(results)}


@router.get("/analytics/export.csv")
async def export_analytics_csv(
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "agent", "viewer")),
):
    conversations = (
        await session.scalars(select(Conversation).order_by(Conversation.created_at.asc()))
    ).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["session_id", "status", "language", "created_at", "updated_at"])
    for conversation in conversations:
        writer.writerow(
            [
                conversation.id,
                conversation.containment_status,
                conversation.language,
                conversation.created_at.isoformat(),
                conversation.updated_at.isoformat(),
            ]
        )
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=enterprise-rag-analytics.csv"},
    )


@router.get("/admin/config")
async def get_bot_config(
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin", "knowledge_manager", "viewer")),
):
    config = await session.get(BotConfiguration, 1)
    return config.settings if config else BotConfigurationRequest().model_dump()


@router.put("/admin/config")
async def update_bot_config(
    payload: BotConfigurationRequest,
    session: AsyncSession = Depends(get_db),
    role: str = Depends(require_roles("admin")),
):
    config = await session.get(BotConfiguration, 1)
    values = payload.model_dump()
    if config is None:
        config = BotConfiguration(id=1, settings=values, updated_by=role)
        session.add(config)
    else:
        config.settings = values
        config.updated_by = role
        config.updated_at = datetime.now(timezone.utc)
    await _audit(session, role, "bot_config.update", "configuration", "1")
    await session.commit()
    return values


@router.get("/admin/audit")
async def list_audit_logs(
    limit: int = Query(default=100, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("admin")),
):
    entries = (
        await session.scalars(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
    ).all()
    return [
        {
            "id": entry.id,
            "actor_role": entry.actor_role,
            "action": entry.action,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "created_at": entry.created_at,
        }
        for entry in entries
    ]
