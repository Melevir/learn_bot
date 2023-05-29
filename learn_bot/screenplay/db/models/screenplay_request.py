from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin


class ScreenplayRequest(TimestampsMixin, Base):
    __tablename__ = "screenplay_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    screenplay_id: Mapped[str] = mapped_column(String(length=256))
    act_id: Mapped[str] = mapped_column(String(length=256))
    context: Mapped[str] = mapped_column(String())
