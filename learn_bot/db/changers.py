from typing import Type

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.db import AssignmentStatusHistory, Curator, Student
from learn_bot.db.base import Base
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.fetchers import fetch_assignments_for_curator
from learn_bot.screenplay.db.models.user import User


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


def drop_all_in_progress_reviews_to_ready_for_review(curator_id: int, session: Session) -> None:
    assignments = fetch_assignments_for_curator(curator_id, [AssignmentStatus.REVIEW_IN_PROGRESS], session)
    for assignment in assignments:
        assignment.status = AssignmentStatus.READY_FOR_REVIEW
        update(assignment, session)
        create(
            AssignmentStatusHistory(new_status=AssignmentStatus.REVIEWED, assignment_id=assignment.id),
            session,
        )


def update_contacts(entity: Student | Curator | User, message: Message, session: Session) -> None:
    if entity.telegram_chat_id is None:
        entity.telegram_chat_id = message.chat.id
        update(entity, session)
