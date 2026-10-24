import csv
import io
import re
import zipfile
from html.parser import HTMLParser
from pathlib import PurePath
from typing import Any
from xml.etree import ElementTree

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import DocumentChunk, DocumentRecord, DocumentVersion
from app.services.guardrails import redact_pii
from app.services.mock_data import MOCK_DOCUMENTS

_SUPPORTED_SUFFIXES = {".pdf", ".docx", ".html", ".htm", ".md", ".markdown", ".csv", ".txt"}
_WHITESPACE = re.compile(r"\s+")


class _VisibleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "iframe", "svg"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "iframe", "svg"}:
            self._hidden_depth = max(0, self._hidden_depth - 1)

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self.parts.append(data)


def extract_document_text(filename: str, content: bytes) -> str:
    safe_name = PurePath(filename.replace("\\", "/")).name
    suffix = PurePath(safe_name).suffix.lower()
    if not safe_name or suffix not in _SUPPORTED_SUFFIXES:
        raise ValueError("Format dokumen tidak didukung.")
    if not content or len(content) > settings.MAX_UPLOAD_BYTES:
        raise ValueError("Ukuran dokumen kosong atau melebihi batas unggahan.")

    if suffix == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Konten tidak cocok dengan format PDF.")
        try:
            reader = PdfReader(io.BytesIO(content), strict=True)
        except PdfReadError as exc:
            raise ValueError("PDF tidak dapat dibaca.") from exc
        if reader.is_encrypted:
            raise ValueError("PDF terenkripsi tidak dapat diproses.")
        if len(reader.pages) > 500:
            raise ValueError("PDF melebihi batas 500 halaman.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == ".docx":
        if not content.startswith(b"PK"):
            raise ValueError("Konten tidak cocok dengan format DOCX.")
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                entries = archive.infolist()
                if len(entries) > 500 or sum(item.file_size for item in entries) > 50_000_000:
                    raise ValueError("DOCX berisi data terkompresi yang melebihi batas.")
                document_xml = archive.read("word/document.xml")
        except zipfile.BadZipFile as exc:
            raise ValueError("DOCX tidak dapat dibaca.") from exc
        except KeyError as exc:
            raise ValueError("DOCX tidak memiliki dokumen utama yang valid.") from exc
        try:
            root = ElementTree.fromstring(document_xml)
        except ElementTree.ParseError as exc:
            raise ValueError("Struktur dokumen DOCX tidak valid.") from exc
        text = " ".join(
            node.text or ""
            for node in root.iter()
            if node.tag.endswith("}t")
        )
    elif suffix in {".html", ".htm"}:
        parser = _VisibleHTMLParser()
        parser.feed(content.decode("utf-8-sig", errors="replace"))
        text = " ".join(parser.parts)
    elif suffix == ".csv":
        decoded = content.decode("utf-8-sig", errors="strict")
        text = "\n".join(" | ".join(row) for row in csv.reader(io.StringIO(decoded)))
    else:
        text = content.decode("utf-8-sig", errors="strict")

    cleaned = _WHITESPACE.sub(" ", redact_pii(text)).strip()
    if not cleaned:
        raise ValueError("Tidak ada teks yang dapat diindeks dari dokumen.")
    return cleaned


def chunk_text(text: str, chunk_size: int = 1_500, overlap: int = 200) -> list[str]:
    if chunk_size < 100 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Pengaturan ukuran chunk tidak valid.")
    normalized = _WHITESPACE.sub(" ", text).strip()
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(start + 1, end - overlap)
    return chunks


async def index_document(
    session: AsyncSession,
    *,
    title: str,
    content: str,
    metadata: dict[str, Any],
    document_id: str | None = None,
) -> tuple[DocumentRecord, int]:
    chunks = chunk_text(content)
    if document_id:
        document = await session.get(DocumentRecord, document_id)
        if document is None:
            raise ValueError("Dokumen tidak ditemukan.")
        version = await session.scalar(
            select(DocumentVersion.version)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
            .limit(1)
        )
        next_version = (version or 0) + 1
        await session.execute(
            DocumentChunk.__table__.delete().where(DocumentChunk.document_id == document_id)
        )
        document.title = title
        document.source_type = metadata["source_type"]
        document.status = "indexed"
        document.metadata_info = metadata
    else:
        document = DocumentRecord(
            title=title,
            source_type=metadata["source_type"],
            status="indexed",
            metadata_info=metadata,
        )
        session.add(document)
        await session.flush()
        next_version = 1

    session.add(
        DocumentVersion(
            document_id=document.id,
            version=next_version,
            title=title,
            content=content,
            metadata_info=metadata,
        )
    )
    session.add_all(
        DocumentChunk(
            document_id=document.id,
            ordinal=ordinal,
            content=chunk,
            metadata_info=metadata,
        )
        for ordinal, chunk in enumerate(chunks)
    )
    await session.flush()
    return document, len(chunks)


async def seed_mock_documents(session: AsyncSession) -> None:
    count = await session.scalar(select(DocumentRecord.id).limit(1))
    if count is not None:
        return
    for source in MOCK_DOCUMENTS:
        metadata = {key: value for key, value in source.items() if key != "content"}
        await index_document(
            session,
            title=source["title"],
            content=source["content"],
            metadata=metadata,
        )
    await session.commit()
