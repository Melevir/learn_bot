from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_bot.db import Course, Curator, Student


def fetch_courses(session: Session) -> list[Course]:
    return list(session.scalars(
        select(Course)
    ).all())


def fetch_curator_by_telegram_nickname(nickname: str, session: Session) -> Curator | None:
    return session.scalar(
        select(Curator).where(
            Curator.telegram_nickname == nickname
        )
    )


def fetch_student_by_telegram_nickname(nickname: str, session: Session) -> Student | None:
    return session.scalar(
        select(Student).where(
            Student.telegram_nickname == nickname
        )
    )
