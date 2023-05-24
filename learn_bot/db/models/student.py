from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin

if TYPE_CHECKING:
    from learn_bot.db.models.assignment import Assignment
    from learn_bot.db.models.group import Group


class Student(TimestampsMixin, Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=256))
    last_name: Mapped[str] = mapped_column(String(length=256))
    telegram_nickname: Mapped[str | None] = mapped_column(String(length=256), unique=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256), unique=True)
    auth_code: Mapped[str | None] = mapped_column(String(length=256), unique=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))

    group: Mapped[Group] = relationship(back_populates="students")
    assignments: Mapped[list[Assignment]] = relationship()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"Student {self.first_name} {self.last_name}"
