from typing import Type

from sqlalchemy.orm import Session

from learn_bot.db.base import Base


def create(model_obj: Base, session: Session) -> Base:
    session.add(model_obj)
    session.commit()
    return model_obj


def update(model_obj: Base, session: Session) -> Base:
    session.add(model_obj)
    session.commit()
    return model_obj


def delete_all_records_from(model: Type[Base], session: Session) -> None:
    session.query(model).delete()
    session.commit()
