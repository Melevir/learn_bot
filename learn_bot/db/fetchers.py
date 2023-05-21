import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_bot.db import (
    Assignment,
    Course,
    Curator,
    Enrollment,
    Group,
    Student,
)
from learn_bot.db.enums import AssignmentStatus
from learn_bot.screenplay.db.models.user import User


def fetch_courses(session: Session) -> list[Course]:
    return list(session.scalars(
        select(Course),
    ).all())


def fetch_curator_by_telegram_nickname(nickname: str | None, session: Session) -> Curator | None:
    if nickname is None:
        return None
    return session.scalar(
        select(Curator).where(
            Curator.telegram_nickname == nickname.lower(),
        ),
    )


def fetch_student_by_chat_id(chat_id: str | None, session: Session) -> Student | None:
    if chat_id is None:
        return None
    return session.scalar(
        select(Student).where(
            Student.telegram_chat_id == str(chat_id),
        ),
    )


def fetch_student_by_telegram_nickname(nickname: str | None, session: Session) -> Student | None:
    if nickname is None:
        return None
    return session.scalar(
        select(Student).where(
            Student.telegram_nickname == nickname.lower(),
        ),
    )


def fetch_assignments_for_curator(
    curator_id: int,
    statuses: list[AssignmentStatus],
    session: Session,
) -> list[Assignment]:
    return list(session.scalars(
        select(Assignment).join(Student).join(Group).filter(
            Assignment.status.in_(statuses),
            Group.curator_id == curator_id,
        ).order_by(Assignment.created_at),
    ).all())


def fetch_oldest_pending_assignment_for_curator(curator_id: int, session: Session) -> Assignment | None:
    return session.scalar(
        select(Assignment).join(Student).join(Group).filter(
            Assignment.status == AssignmentStatus.READY_FOR_REVIEW,
            Group.curator_id == curator_id,
        ).order_by(Assignment.created_at).limit(1),
    )


def fetch_assignment_by_id(assignment_id: int, session: Session) -> Assignment | None:
    return session.scalar(
        select(Assignment).where(
            Assignment.id == assignment_id,
        ),
    )


def fetch_role_by_user(user: User, session: Session) -> str | None:
    curator = fetch_curator_by_telegram_nickname(user.telegram_nickname, session)
    student = (
        fetch_student_by_telegram_nickname(user.telegram_nickname, session)
        or fetch_student_by_chat_id(user.telegram_chat_id, session)
    )
    return "curator" if curator is not None else "student" if student is not None else None


def fetch_active_groups_for_curator(curator: Curator, session: Session) -> list[Group]:
    return list(session.scalars(
        select(Group).join(Enrollment).filter(
            Group.curator_id == curator.id,
            Enrollment.date_end >= datetime.date.today(),
        ).order_by(Group.created_at),
    ).all())


def fetch_students_in_group(group: Group, session: Session) -> list[Student]:
    return list(session.scalars(
        select(Student).filter(
            Student.group_id == group.id,
        ).order_by(Student.created_at),
    ).all())


def fetch_all_assignments_for_student_in_period(
    student: Student,
    date_from: datetime.date,
    date_to: datetime.date,
    session: Session,
) -> list[Assignment]:
    return list(session.scalars(
        select(Assignment).filter(
            Assignment.student_id == student.id,
            Assignment.created_at >= date_from,
            Assignment.created_at <= date_to,
        ).order_by(Assignment.created_at),
    ).all())
