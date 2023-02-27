from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db import Student
from learn_bot.db.base import Base


class Assignment(Base):
    __tablename__ = "assignment"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(length=512))

    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))

    student: Mapped[Student] = relationship(back_populates="assignments")

    def __repr__(self) -> str:
        return f"Assignment #{self.id} from student {self.student_id}"
