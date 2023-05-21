from __future__ import annotations

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from learn_bot.db.base import Base
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.mixins import TimestampsMixin


class AssignmentStatusHistory(TimestampsMixin, Base):
    __tablename__ = "assignment_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    new_status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus))

    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignment.id"))
