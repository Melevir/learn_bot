from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin
from learn_bot.db.models.curator import Curator
from learn_bot.db.models.enrollment import Enrollment

if TYPE_CHECKING:
    from learn_bot.db.models.student import Student


class Group(TimestampsMixin, Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))

    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollment.id"))
    curator_id: Mapped[int] = mapped_column(ForeignKey("curator.id"))

    enrollment: Mapped[Enrollment] = relationship(back_populates="groups")
    curator: Mapped[Curator] = relationship(back_populates="groups")
    students: Mapped[list[Student]] = relationship()

    def __repr__(self) -> str:
        return f"Group #{self.id} of enrollment {self.enrollment_id}"
