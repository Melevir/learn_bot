from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin
from learn_bot.db.models.group import Group

if TYPE_CHECKING:
    from learn_bot.db.models.assignment import Assignment


class Student(TimestampsMixin, Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=256))
    last_name: Mapped[str] = mapped_column(String(length=256))
    telegram_nickname: Mapped[str | None] = mapped_column(String(length=256))
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))

    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))

    group: Mapped[Group] = relationship(back_populates="students")
    assignments: Mapped[list[Assignment]] = relationship()

    def __repr__(self) -> str:
        return f"Student {self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
