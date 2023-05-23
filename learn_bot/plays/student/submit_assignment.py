from typing import Mapping, cast

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Assignment, AssignmentStatusHistory, Curator, Student
from learn_bot.db.changers import create
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.utils.urls import (
    is_github_pull_request_url,
    is_github_repo_url,
    is_url_accessible,
    is_valid_github_url,
)
from learn_bot.screenplay.custom_types import ActResult
from learn_bot.screenplay.db.models.user import User
from learn_bot.services.assignment import handle_new_assignment


def intro(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    return ActResult(
        screenplay_id=context["screenplay_id"],
        act_id="create_assignment",
        messages=["Скажи ссылку на Гитхаб с работой для проверки. Если у тебя несколько работ, сдавай их по одной"],
    )


def create_assignment(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    assert student

    assignment_url = message.text.rstrip("/")
    if not is_valid_github_url(assignment_url):
        return ActResult(
            screenplay_id=context["screenplay_id"],
            act_id="create_assignment",
            messages=[
                "Это не похоже на ссылку на Гитхаб. Скажи ссылку на Гитхаб с работой для проверки",
                "Если у тебя несколько работ, сдавай их по одной",
            ],
        )
    elif not is_url_accessible(assignment_url):
        return ActResult(
            screenplay_id=context["screenplay_id"],
            act_id="create_assignment",
            messages=[
                (
                    "Я не вижу по этой ссылке работы. Пожалуйcта, убедись, что ссылка правильная и сделай "
                    "репозиторий на Гитхабе публичным"
                ),
            ],
        )

    curator_name = student.group.curator.first_name
    messages = (
        [
            (
                "На проверку лучше сдавать ссылки в одном из двух форматов\n"
                "- ссылка на пул-реквест (например: https://github.com/Melevir/flake8-functions-names/pull/13)\n"
                "- ссылка на репозиторий (например: https://github.com/Melevir/flake8-functions-names)"
            ),
            "Твоя ссылка не похожа ни на один из этих вариантов",
            "Эту работу я записал и куратор её проверит",
            "В следующий раз постарайся сдать ссылку в одном из форматов выше, пожалуйста",
            "Если хочешь сдать ещё одну работу, повтори команду /submit",
        ]
        if not is_github_pull_request_url(assignment_url) and not is_github_repo_url(assignment_url)
        else [
            f"Записал! Дам знать, как {curator_name} проверит твою работу",
            "Если хочешь сдать ещё одну работу, повтори команду /submit",
        ]
    )
    assignment = cast(Assignment, create(
        Assignment(url=assignment_url, student_id=student.id, status=AssignmentStatus.READY_FOR_REVIEW),
        session,
    ))
    create(
        AssignmentStatusHistory(new_status=AssignmentStatus.READY_FOR_REVIEW, assignment_id=assignment.id),
        session,
    )
    handle_new_assignment(assignment, bot)
    return ActResult(
        screenplay_id=None,
        act_id=None,
        messages=messages,
        is_screenplay_over=True,
    )
