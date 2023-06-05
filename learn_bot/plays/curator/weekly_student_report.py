import dataclasses
import datetime
import operator
import random
from typing import Mapping

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Curator, Group, Student
from learn_bot.db.fetchers import (
    fetch_active_groups_for_curator,
    fetch_all_assignments_for_student_in_period,
    fetch_students_in_group,
)
from learn_bot.enums import Gender
from learn_bot.screenplay.custom_types import ActResult
from learn_bot.screenplay.db.models.user import User
from learn_bot.services.gender_guesser import guess_gender


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class AssignmentGroupStat:
    course_name: str
    date_from: datetime.date
    date_to: datetime.date
    students_stat: Mapping[tuple[str, str], int]


def show_weekly_students_report(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    date_from, date_to = _fetch_current_week_dates()
    assert curator
    groups = fetch_active_groups_for_curator(curator, session)
    group_stats = [_compose_assignment_stat_for_group(g, date_from, date_to, session) for g in groups]

    message = _compose_assignment_stat_message(group_stats) if groups else "У вас нет активных групп"

    return ActResult(
        messages=[message],
        screenplay_id=None,
        act_id=None,
        is_screenplay_over=True,
    )


def _fetch_current_week_dates() -> tuple[datetime.date, datetime.date]:
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday()), today + datetime.timedelta(days=1)


def _compose_assignment_stat_for_group(
    group: Group,
    date_from: datetime.date,
    date_to: datetime.date,
    session: Session,
) -> AssignmentGroupStat:
    students_stat = {}
    for student in fetch_students_in_group(group, session):
        assignments = fetch_all_assignments_for_student_in_period(student, date_from, date_to, session)
        students_stat[(student.first_name, student.last_name)] = len(assignments)
    return AssignmentGroupStat(
        course_name=group.enrollment.course.title,
        date_from=date_from,
        date_to=date_to,
        students_stat=students_stat,
    )


def _compose_assignment_stat_message(group_stats: list[AssignmentGroupStat]) -> str:
    lines = []
    for stat in group_stats:
        lines.append(f"Статистика в твоей группе курса {stat.course_name} с {stat.date_from} по {stat.date_to}:")
        students_stat = sorted(stat.students_stat.items(), key=operator.itemgetter(1), reverse=True)
        for (student_first_name, student_last_name), submitted_assignments_num in students_stat:
            student_full_name = f"{student_first_name} {student_last_name}"
            status = random.choice("👍🥳😎🤓💯") if submitted_assignments_num else random.choice("👎😕😖😡😨💣")
            verb = (
                "сдал"
                if guess_gender(student_first_name, student_last_name) == Gender.MALE
                else "сдала"
            )
            lines.append(f" - {student_full_name} {verb} {submitted_assignments_num} работ {status}")
        lines.append("")
    return "\n".join(lines)
