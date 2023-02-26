from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.models.enrollment import Enrollment


class Curator(Base):
    __tablename__ = "curator"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=256))
    last_name: Mapped[str] = mapped_column(String(length=256))
    telegram_nickname: Mapped[str] = mapped_column(String(length=256))
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))

    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollment.id"))

    enrollment: Mapped[Enrollment] = relationship(back_populates="curators")

    def __repr__(self) -> str:
        return f"Curator {self.first_name} {self.last_name}"
