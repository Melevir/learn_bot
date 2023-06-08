from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.mixins import TimestampsMixin

if TYPE_CHECKING:
    from learn_bot.db import Student


class Assignment(TimestampsMixin, Base):
    __tablename__ = "assignment"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(length=512))
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus))
    curator_feedback: Mapped[str | None] = mapped_column(Text(), nullable=True)
    review_message_id_in_curator_chat: Mapped[str | None] = mapped_column(String(length=512))
    review_message_id_in_student_chat: Mapped[str | None] = mapped_column(String(length=512))

    is_rereview_for: Mapped[int | None] = mapped_column(ForeignKey("assignment.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))

    student: Mapped[Student] = relationship(back_populates="assignments")

    def __repr__(self) -> str:
        return f"Assignment #{self.id} from student {self.student_id}"
