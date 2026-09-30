from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

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