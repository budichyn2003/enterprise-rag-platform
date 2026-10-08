from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON
from datetime import datetime
import os
import uuid

# 1. Ambil DATABASE_URL dari file .env
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 2. Modifikasi skema URL agar menggunakan driver asyncpg (Wajib untuk Async SQLAlchemy)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Jika .env kosong/tidak ada DATABASE_URL, gunakan SQLite async sebagai cadangan agar tidak crash
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# 3. Buat Async Engine yang dicari oleh app/main.py baris 20
engine = create_async_engine(DATABASE_URL, echo=False)

# 4. Buat sessionmaker versi Async
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 5. Deklarasi Base Model
Base = declarative_base()

# =====================================================================
# SKEMA TABEL KAMU (TETAP DIPERTAHANKAN)
# =====================================================================

class DocumentRecord(Base):
    """Menyimpan metadata dari dokumen yang di-ingest (FR-KM-05)"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    status = Column(String, default="queued") 
    metadata_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    """Menyimpan sesi percakapan untuk konteks memori dan analitik (FR-RAG-04)"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    containment_status = Column(String, default="active") # active, resolved, escalated
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    """Menyimpan log chat individual termasuk sitasi (FR-AN-03)"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False) # user, ai, agent
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
