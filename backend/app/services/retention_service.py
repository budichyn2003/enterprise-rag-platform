from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import ChatFeedback, Conversation, HandoffTicket, Message


async def purge_expired_conversations(
    session: AsyncSession,
    retention_days: int,
) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    expired_ids = select(Conversation.id).where(Conversation.created_at < cutoff)
    await session.execute(
        delete(ChatFeedback).where(ChatFeedback.conversation_id.in_(expired_ids))
    )
    await session.execute(
        delete(HandoffTicket).where(HandoffTicket.conversation_id.in_(expired_ids))
    )
    await session.execute(delete(Message).where(Message.conversation_id.in_(expired_ids)))
    result = await session.execute(delete(Conversation).where(Conversation.id.in_(expired_ids)))
    return max(result.rowcount or 0, 0)
