import datetime
from typing import Mapping

from pyairtable import Table
from sqlalchemy.orm import Session

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Course, Enrollment, Curator, Group, Student
from learn_bot.db.changers import create


def process_course(session: Session) -> Course:
    course = Course(title="Learn Python")
    create(course, session)
    return course


def process_enrollment(
    course_num_to_import: int,
    course_id: int,
    session: Session,
    config: BotConfig,
) -> Mapping[str, int]:
    enrollments_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_course_table_id)
    enrollments = enrollments_table.all()
    enrollment = [e for e in enrollments if e["fields"].get("course_number") == str(course_num_to_import)][0]
    db_enrollment = Enrollment(
        number=course_num_to_import,
        date_start=datetime.date.fromisoformat(enrollment["fields"]["start_date"]),
        date_end=datetime.date.fromisoformat(enrollment["fields"]["end_date"]),
        course_id=course_id,
    )
    create(db_enrollment, session)
    return {enrollment["id"]: db_enrollment.id}


def process_curators(session: Session, config: BotConfig) -> Mapping[str, int]:
    curators_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_curators_table_id)
    curators = curators_table.all()
    curators_map = {}
    for curator in curators:
        first_name, last_name = curator["fields"]["courator"].strip().split(" ")
        db_curator = Curator(
            first_name=first_name,
            last_name=last_name,
            telegram_nickname=curator["fields"]["telegram"].strip("@-"),
        )
        create(db_curator, session)
        curators_map[curator["id"]] = db_curator.id
    return curators_map


def process_groups(
    enrollments_map: Mapping[str, int],
    curators_map: Mapping[str, int],
    session: Session,
    config: BotConfig,
) -> Mapping[str, int]:
    groups_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_groups_table_id)
    groups = [g for g in groups_table.all() if "course" in g["fields"] and g["fields"]["course"][0] in enrollments_map]
    groups_map = {}
    for group in groups:
        db_group = Group(
            enrollment_id=enrollments_map[group["fields"]["course"][0]],
            curator_id=curators_map[group["fields"]["courator"][0]],
        )
        create(db_group, session)
        groups_map[group["id"]] = db_group.id
    return groups_map


def process_students(
    groups_map: Mapping[str, int],
    session: Session,
    config: BotConfig,
) -> None:
    students_table = Table(config.airtable_api_token, config.airtable_database_id, config.airtable_students_table_id)
    students = [s for s in students_table.all() if "group" in s["fields"] and s["fields"]["group"][0] in groups_map]
    for student in students:
        telegram_nickname = (
            (student["fields"]["telegram"].strip('-@') or None)
            if "telegram" in student["fields"]
            else None
        )
        db_student = Student(
            first_name=student["fields"]["first_name"],
            last_name=student["fields"]["last_name"],
            telegram_nickname=telegram_nickname,
            group_id=groups_map[student["fields"]["group"][0]],
        )
        create(db_student, session)


def run(bot: Bot, config: BotConfig) -> None:
    course_num_to_import = 28
    with bot.get_session() as session:
        course = process_course(session)
        enrollments_map = process_enrollment(course_num_to_import, course.id, session, config)
        curators_map = process_curators(session, config)
        groups_map = process_groups(enrollments_map, curators_map, session, config)
        process_students(groups_map, session, config)
