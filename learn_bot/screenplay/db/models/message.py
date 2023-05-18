from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin


class ChatMessage(TimestampsMixin, Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))
    from_user_id: Mapped[str | None] = mapped_column(String(length=256))
    message: Mapped[str] = mapped_column(String(length=256))

    def __repr__(self) -> str:
        return self.message
