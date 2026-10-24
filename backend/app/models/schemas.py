from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

class DocumentMetadata(BaseModel):
    source_type: Literal["upload", "confluence", "google_drive", "mock"] = "upload"
    category: str = Field(default="general", min_length=1, max_length=80)
    language: Literal["id", "en"] = "id"
    product: str = Field(default="general", min_length=1, max_length=80)
    region: str = Field(default="global", min_length=1, max_length=80)
    sensitivity: Literal["public", "internal", "restricted"] = "public"
    source_url: HttpUrl | None = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: Literal["queued", "processing", "indexed", "failed"]
    chunks_processed: int = 0
    message: str

class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=36, max_length=36)
    message: str = Field(min_length=1, max_length=4_000)
    language: Literal["id", "en"] = "id"
    product: str | None = Field(default=None, max_length=80)
    region: str | None = Field(default=None, max_length=80)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Pesan tidak boleh kosong.")
        return value.strip()

class Citation(BaseModel):
    document_id: str
    title: str
    url: str | None = None

class ChatResponse(BaseModel):
    session_id: str
    message_id: str | None = None
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)
    needs_escalation: bool = False
    handoff_id: str | None = None

class DocumentUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_base64: str = Field(min_length=1, max_length=7_000_000)
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)

class FeedbackRequest(BaseModel):
    message_id: str = Field(min_length=36, max_length=36)
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)

class HandoffRequest(BaseModel):
    reason: str = Field(default="customer_requested", min_length=1, max_length=100)

class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    metadata: DocumentMetadata | None = None

class BotConfigurationRequest(BaseModel):
    confidence_threshold: float = Field(default=0.35, ge=0, le=1)
    max_context_chunks: int = Field(default=4, ge=1, le=10)
    allowed_topics: list[str] = Field(
        default_factory=lambda: ["returns", "shipping", "support", "accounts", "billing"],
        min_length=1,
        max_length=50,
    )

    @field_validator("allowed_topics")
    @classmethod
    def validate_allowed_topics(cls, value: list[str]) -> list[str]:
        normalized = [topic.strip().casefold() for topic in value]
        if any(not topic or len(topic) > 80 for topic in normalized):
            raise ValueError("Setiap topik harus memiliki 1 sampai 80 karakter.")
        return list(dict.fromkeys(normalized))