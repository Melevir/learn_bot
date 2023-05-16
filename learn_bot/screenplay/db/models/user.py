from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin


class User(TimestampsMixin, Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(length=256))
    last_name: Mapped[str | None] = mapped_column(String(length=256))
    telegram_nickname: Mapped[str | None] = mapped_column(String(length=256))
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))

    active_screenplay_id: Mapped[str | None] = mapped_column(String(length=256))
    active_act_id: Mapped[str | None] = mapped_column(String(length=256))

    def __repr__(self) -> str:
        return f"User {self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
