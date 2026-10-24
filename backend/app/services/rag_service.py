import re
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import DocumentChunk, DocumentRecord
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.services.guardrails import (
    detect_prompt_injection,
    detect_restricted_topic,
    moderate_output,
    redact_pii,
)

_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP_WORDS = {
    "a", "ada", "apa", "bagaimana", "dari", "di", "dan", "dengan", "for", "how",
    "i", "in", "is", "it", "ke", "my", "of", "on", "or", "saya", "the", "to",
    "untuk", "what", "when", "where", "yang",
}
_SYNONYMS = {
    "refund": {"pengembalian", "dana", "refund"},
    "pengembalian": {"refund", "returns", "return"},
    "return": {"refund", "pengembalian", "returns"},
    "delivery": {"pengiriman", "delivery", "shipping"},
    "shipping": {"pengiriman", "delivery", "shipping"},
    "pengiriman": {"delivery", "shipping"},
    "lama": {"hari", "waktu", "durasi", "long", "days"},
    "password": {"kata", "sandi", "password"},
    "kata": {"password", "sandi"},
    "invoice": {"tagihan", "invoice", "billing"},
    "tagihan": {"invoice", "billing", "tagihan"},
}


def _tokens(text: str) -> set[str]:
    text = re.sub(r"\[REDACTED(?:_[A-Z]+)?\]", " ", text, flags=re.IGNORECASE)
    return {
        token
        for token in _TOKEN.findall(text.casefold())
        if len(token) > 1 and token not in _STOP_WORDS
    }


def _expanded_query(query: str) -> set[str]:
    tokens = _tokens(query)
    expanded = set(tokens)
    for token in tokens:
        expanded.update(_SYNONYMS.get(token, set()))
    return expanded


class RAGService:
    async def retrieve_documents(
        self,
        session: AsyncSession,
        query: str,
        *,
        language: str,
        product: str | None = None,
        region: str | None = None,
        limit: int = 4,
        allowed_topics: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        records = (
            await session.execute(
                select(DocumentChunk, DocumentRecord)
                .join(DocumentRecord, DocumentRecord.id == DocumentChunk.document_id)
                .where(DocumentRecord.status == "indexed")
                .order_by(DocumentChunk.document_id, DocumentChunk.ordinal)
                .limit(5_000)
            )
        ).all()
        query_terms = _expanded_query(query)
        if not query_terms:
            return []

        candidates: list[dict[str, Any]] = []
        for chunk, document in records:
            metadata = chunk.metadata_info or document.metadata_info or {}
            if metadata.get("sensitivity", "public") != "public":
                continue
            if allowed_topics is not None and metadata.get("category", "general").casefold() not in allowed_topics:
                continue
            if metadata.get("language", language) not in {language, "id", "en"}:
                continue
            if product and metadata.get("product", "general") not in {product, "general"}:
                continue
            if region and metadata.get("region", "global") not in {region, "global"}:
                continue

            body_terms = _tokens(chunk.content)
            title_terms = _tokens(document.title)
            overlap = len(query_terms & body_terms) / len(query_terms)
            title_overlap = len(query_terms & title_terms) / len(query_terms)
            phrase_match = 1.0 if query.casefold() in chunk.content.casefold() else 0.0
            language_match = 1.0 if metadata.get("language", "id") == language else 0.0
            score = min(
                1.0,
                overlap * 0.65 + title_overlap * 0.15 + phrase_match * 0.1 + language_match * 0.1,
            )
            if overlap > 0:
                candidates.append(
                    {
                        "document_id": document.id,
                        "title": document.title,
                        "content": chunk.content,
                        "url": metadata.get("source_url"),
                        "score": score,
                    }
                )
        candidates.sort(key=lambda item: item["score"], reverse=True)

        # Keep one excerpt per source so duplicate chunks do not crowd out citations.
        selected: list[dict[str, Any]] = []
        seen_documents: set[str] = set()
        for candidate in candidates:
            if candidate["document_id"] in seen_documents:
                continue
            seen_documents.add(candidate["document_id"])
            selected.append(candidate)
            if len(selected) >= limit:
                break
        return selected

    async def generate_response(
        self,
        session: AsyncSession,
        request: ChatRequest,
        chat_history: list[dict[str, Any]],
        *,
        confidence_threshold: float = 0.35,
        max_context_chunks: int = 4,
        allowed_topics: list[str] | None = None,
    ) -> ChatResponse:
        session_id = request.session_id or str(uuid4())
        safe_message = redact_pii(request.message)
        if detect_prompt_injection(safe_message):
            return ChatResponse(
                session_id=session_id,
                answer=(
                    "Maaf, saya tidak dapat membantu permintaan tersebut. "
                    "Saya akan menghubungkan Anda dengan tim support."
                    if request.language == "id"
                    else "I can't help with that request. I'll connect you with support."
                ),
                confidence_score=0,
                needs_escalation=True,
            )
        if detect_restricted_topic(safe_message):
            return ChatResponse(
                session_id=session_id,
                answer=(
                    "Topik ini memerlukan bantuan spesialis. Saya akan menghubungkan Anda "
                    "dengan tim support."
                    if request.language == "id"
                    else "This topic needs specialist support. I'll connect you with our team."
                ),
                confidence_score=0,
                needs_escalation=True,
            )

        query = safe_message
        if chat_history and re.search(
            r"(?i)\b(?:berapa lama|kapan|itu|tersebut|how long|when|that|it)\b", safe_message
        ):
            previous_user = next(
                (item.get("content", "") for item in reversed(chat_history) if item.get("role") == "user"),
                "",
            )
            query = f"{previous_user} {safe_message}".strip()

        documents = await self.retrieve_documents(
            session,
            query,
            language=request.language,
            product=request.product,
            region=request.region,
            limit=max_context_chunks,
            allowed_topics=allowed_topics,
        )
        best_score = documents[0]["score"] if documents else 0.0
        if not documents or best_score < confidence_threshold:
            return ChatResponse(
                session_id=session_id,
                answer=(
                    "Maaf, saya belum menemukan informasi yang cukup di basis pengetahuan. "
                    "Saya akan membantu menghubungkan Anda dengan agent."
                    if request.language == "id"
                    else "I couldn't find enough information in the knowledge base. "
                    "I'll help connect you with an agent."
                ),
                confidence_score=round(best_score, 3),
                needs_escalation=True,
            )

        top_document = documents[0]
        if request.language == "id":
            answer = f"Berdasarkan {top_document['title']}: {top_document['content']}"
        else:
            answer = f"According to {top_document['title']}: {top_document['content']}"
        return ChatResponse(
            session_id=session_id,
            answer=moderate_output(answer),
            citations=[
                Citation(
                    document_id=document["document_id"],
                    title=document["title"],
                    url=document["url"],
                )
                for document in documents
            ],
            confidence_score=round(best_score, 3),
            needs_escalation=best_score < confidence_threshold,
        )


rag_service = RAGService()
