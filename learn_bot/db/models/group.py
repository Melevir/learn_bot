from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_bot.db.base import Base
from learn_bot.db.models.curator import Curator
from learn_bot.db.models.enrollment import Enrollment


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(length=256))

    enrollment_id: Mapped[int] = mapped_column(ForeignKey("enrollment.id"))
    curator_id: Mapped[int] = mapped_column(ForeignKey("curator.id"))

    enrollment: Mapped[Enrollment] = relationship(back_populates="curators")
    curator: Mapped[Curator] = relationship(back_populates="groups")

    def __repr__(self) -> str:
        return f"Group #{self.id} of enrollment {self.enrollment_id}"
