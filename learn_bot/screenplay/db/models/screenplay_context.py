from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from learn_bot.db.base import Base
from learn_bot.db.mixins import TimestampsMixin


class ScreenplayContext(TimestampsMixin, Base):
    __tablename__ = "screenplay_context"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    screenplay_id: Mapped[str] = mapped_column(String(length=256))
    data: Mapped[dict[str, str]] = mapped_column(JSON(), server_default="{}")
