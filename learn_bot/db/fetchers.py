from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_bot.db import Course, Curator, Student, Assignment, Group
from learn_bot.db.enums import AssignmentStatus


def fetch_courses(session: Session) -> list[Course]:
    return list(session.scalars(
        select(Course),
    ).all())


def fetch_curator_by_telegram_nickname(nickname: str, session: Session) -> Curator | None:
    return session.scalar(
        select(Curator).where(
            Curator.telegram_nickname == nickname,
        )
    )


def fetch_student_by_telegram_nickname(nickname: str, session: Session) -> Student | None:
    return session.scalar(
        select(Student).where(
            Student.telegram_nickname == nickname,
        )
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
