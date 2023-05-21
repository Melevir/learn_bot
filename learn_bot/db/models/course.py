from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin

if TYPE_CHECKING:
    from learn_bot.db import Enrollment


class Course(TimestampsMixin, Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=512))

    enrollments: Mapped[list[Enrollment]] = relationship()

    def __repr__(self) -> str:
        return self.title
