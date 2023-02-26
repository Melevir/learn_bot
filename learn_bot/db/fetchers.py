from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_bot.db import Course


def fetch_courses(session: Session) -> list[Course]:
    return list(session.scalars(
        select(Course)
    ).all())
