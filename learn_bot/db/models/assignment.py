from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db import Student
from learn_bot.db.base import Base
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.mixins import TimestampsMixin


class Assignment(TimestampsMixin, Base):
    __tablename__ = "assignment"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(length=512))
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus))
    curator_feedback: Mapped[str | None] = mapped_column(Text(), nullable=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))

    student: Mapped[Student] = relationship(back_populates="assignments")

    def __repr__(self) -> str:
        return f"Assignment #{self.id} from student {self.student_id}"
