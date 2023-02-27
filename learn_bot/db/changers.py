from sqlalchemy.orm import Session

from learn_bot.db.base import Base


def create(model_obj: Base, session: Session) -> None:
    session.add(model_obj)
    session.commit()


def update(model_obj: Base, session: Session) -> None:
    session.add(model_obj)
    session.commit()
