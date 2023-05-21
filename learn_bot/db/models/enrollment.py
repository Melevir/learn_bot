from __future__ import annotations
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db import Course
from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin

if TYPE_CHECKING:
    from learn_bot.db import Group


class Enrollment(TimestampsMixin, Base):
    __tablename__ = "enrollment"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column()
    date_start: Mapped[datetime.date] = mapped_column()
    date_end: Mapped[datetime.date] = mapped_column()
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))

    course: Mapped[Course] = relationship(back_populates="enrollments")
    groups: Mapped[list[Group]] = relationship()

    @property
    def is_active(self) -> bool:
        today = datetime.date.today()
        return self.date_start <= today <= self.date_end

    def __repr__(self) -> str:
        return f"Enrollment #{self.number} of {self.course}"
