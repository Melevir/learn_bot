import datetime
from typing import Mapping, cast

from pyairtable import Table
from sqlalchemy.orm import Session

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Course, Curator, Enrollment, Group, Student
from learn_bot.db.changers import create_or_update


def process_course(session: Session, is_advanced: bool) -> Course:
    title = "Learn Python Advanced" if is_advanced else "Learn Python"
    course = Course(title=title)
    return cast(Course, create_or_update(course, session))


def process_enrollment(
    course_num_to_import: int,
    course_slug_to_import: str,
    course_id: int,
    session: Session,
    config: BotConfig,
) -> Mapping[str, int]:
    assert config.airtable_api_token
    assert config.airtable_database_id
    assert config.airtable_course_table_id
    enrollments_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_course_table_id)
    enrollments = enrollments_table.all()  # type: ignore[no-untyped-call]
    enrollment = [e for e in enrollments if e["fields"].get("course_number") == course_slug_to_import][0]
    db_enrollment = Enrollment(
        number=course_num_to_import,
        date_start=datetime.date.fromisoformat(enrollment["fields"]["start_date"]),
        date_end=datetime.date.fromisoformat(enrollment["fields"]["end_date"]),
        course_id=course_id,
    )
    db_enrollment = cast(Enrollment, create_or_update(db_enrollment, session))
    return {enrollment["id"]: db_enrollment.id}


def process_curators(session: Session, config: BotConfig) -> Mapping[str, int]:
    assert config.airtable_api_token
    assert config.airtable_database_id
    assert config.airtable_curators_table_id

    curators_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_curators_table_id)
    curators = curators_table.all()  # type: ignore[no-untyped-call]
    curators_map = {}
    for curator in curators:
        telegram_nickname = _clear_tg_nickname(curator["fields"]["telegram"])
        first_name, last_name = curator["fields"]["courator"].strip().split(" ")
        db_curator = Curator(
            first_name=first_name,
            last_name=last_name,
            telegram_nickname=telegram_nickname,
        )
        db_curator = cast(Curator, create_or_update(db_curator, session))
        curators_map[curator["id"]] = db_curator.id
    return curators_map


def process_groups(
    enrollments_map: Mapping[str, int],
    curators_map: Mapping[str, int],
    session: Session,
    config: BotConfig,
) -> Mapping[str, int]:
    assert config.airtable_api_token
    assert config.airtable_database_id
    assert config.airtable_groups_table_id

    groups_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_groups_table_id)
    groups = [
        g for g in groups_table.all()  # type: ignore[no-untyped-call]
        if "course" in g["fields"] and g["fields"]["course"][0] in enrollments_map]
    groups_map = {}
    for group in groups:
        db_group = Group(
            enrollment_id=enrollments_map[group["fields"]["course"][0]],
            curator_id=curators_map[group["fields"]["courator"][0]],
        )
        db_group = cast(Group, create_or_update(db_group, session))
        groups_map[group["id"]] = db_group.id
    return groups_map


def process_students(
    groups_map: Mapping[str, int],
    session: Session,
    config: BotConfig,
) -> None:
    assert config.airtable_api_token
    assert config.airtable_database_id
    assert config.airtable_students_table_id

    students_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_students_table_id)
    students = [
        s for s in students_table.all()  # type: ignore[no-untyped-call]
        if "group" in s["fields"] and s["fields"]["group"][0] in groups_map
    ]
    for student in students:
        telegram_nickname = (  # noqa: ECE001
            (student["fields"]["telegram"].strip("-@").lower() or None)
            if "telegram" in student["fields"]
            else None
        )
        db_student = Student(
            first_name=student["fields"]["first_name"],
            last_name=student["fields"]["last_name"],
            telegram_nickname=telegram_nickname,
            group_id=groups_map[student["fields"]["group"][0]],
            auth_code=student["fields"]["bot_auth_code"],
            email=student["fields"]["email"],
            timepad_id=str(student["fields"]["timepad_id"]),
        )
        db_student = cast(Student, create_or_update(db_student, session))


def _clear_tg_nickname(raw_tg_nickname: str) -> str:
    if raw_tg_nickname.startswith("https://t.me/"):
        raw_tg_nickname = raw_tg_nickname.split("/")[-1]
    return raw_tg_nickname.lower().strip("@-")


def run(bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        for course_num_to_import, course_slug_to_import, is_advanced in [
            (29, "29", False),
        ]:
            course = process_course(session, is_advanced)
            enrollments_map = process_enrollment(
                course_num_to_import,
                course_slug_to_import,
                course.id,
                session,
                config,
            )
            curators_map = process_curators(session, config)
            groups_map = process_groups(enrollments_map, curators_map, session, config)
            process_students(groups_map, session, config)
