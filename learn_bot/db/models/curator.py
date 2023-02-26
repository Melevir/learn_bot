from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base


class Curator(Base):
    __tablename__ = "curator"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=256))
    last_name: Mapped[str] = mapped_column(String(length=256))
    telegram_nickname: Mapped[str] = mapped_column(String(length=256))
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))

    groups: Mapped[list["Group"]] = relationship()

    def __repr__(self) -> str:
        return f"Curator {self.first_name} {self.last_name}"
