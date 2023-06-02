from typing import Any, Callable, Mapping, Type

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.db import AssignmentStatusHistory, Course, Curator, Enrollment, Group, Student
from learn_bot.db.base import Base
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.fetchers import (
    fetch_assignments_for_curator,
    find_similar_course,
    find_similar_curator,
    find_similar_enrollment,
    find_similar_group,
    find_similar_student,
)
from learn_bot.screenplay.db.models.user import User


def get_or_create(model_obj: Base, session: Session) -> Base:
    finders_map: Mapping[Type[Base], Callable[[Any, Session], Any]] = {
        Curator: find_similar_curator,
        Course: find_similar_course,
        Enrollment: find_similar_enrollment,
        Group: find_similar_group,
        Student: find_similar_student,
    }
    assert type(model_obj) in finders_map
    if existing_object := finders_map[type(model_obj)](model_obj, session):
        return existing_object
    return create(model_obj, session)


def create_or_update(model_obj: Base, session: Session) -> Base:
    finders_map: Mapping[Type[Base], Callable[[Any, Session], Any]] = {
        Curator: find_similar_curator,
        Course: find_similar_course,
        Enrollment: find_similar_enrollment,
        Group: find_similar_group,
        Student: find_similar_student,
    }
    assert type(model_obj) in finders_map
    if existing_object := finders_map[type(model_obj)](model_obj, session):
        copy_all_fields_from_another_object(existing_object, model_obj)
        return update(existing_object, session)
    return create(model_obj, session)


def copy_all_fields_from_another_object(copy_to: Base, copy_from: Base) -> None:
    attrs_to_skip = {"id", "created_at", "updated_at", "telegram_chat_id"}
    attrs_names = type(copy_from).__mapper__.columns.keys()
    for attr_name in attrs_names:
        if attr_name in attrs_to_skip:
            continue
        setattr(copy_to, attr_name, getattr(copy_from, attr_name))


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
