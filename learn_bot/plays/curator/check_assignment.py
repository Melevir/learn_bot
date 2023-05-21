from typing import Mapping

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import AssignmentStatusHistory, Curator, Student
from learn_bot.db.changers import create, update
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.fetchers import (
    fetch_assignment_by_id,
    fetch_assignments_for_curator,
    fetch_oldest_pending_assignment_for_curator,
)
from learn_bot.db.utils.urls import is_github_pull_request_url
from learn_bot.markups import (
    compose_curator_assignment_pull_request_check_markup,
    compose_curator_assignments_list_markup,
)
from learn_bot.screenplay.custom_types import ActResult
from learn_bot.screenplay.db.models.user import User
from learn_bot.services.assignment import handle_assignment_checked


def list_pending_assignments(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    assert curator

    if assignments := fetch_assignments_for_curator(
        curator.id,
        statuses=[AssignmentStatus.READY_FOR_REVIEW],
        session=session,
    ):
        return ActResult(
            messages=[f"У тебя {len(assignments)} заданий на проверку"],
            screenplay_id="curator.check_assignment",
            act_id="start",
            replay_markup=compose_curator_assignments_list_markup(),
        )
    else:
        return ActResult(
            messages=["У тебя нет заданий на проверку"],
            screenplay_id=None,
            act_id=None,
            is_screenplay_over=True,
        )


def start_assignments_check(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    if message.text == "Позже":
        return ActResult(messages=["Тогда до скорого"], screenplay_id=None, act_id=None, is_screenplay_over=True)
    else:
        return ActResult(screenplay_id="curator.check_assignment", act_id="check", play_next_act_now=True)


def check_oldest_pending_assignment(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    assert curator
    assignment = fetch_oldest_pending_assignment_for_curator(curator.id, session=session)
    assert assignment

    assignment.status = AssignmentStatus.REVIEW_IN_PROGRESS
    update(assignment, session)
    create(
        AssignmentStatusHistory(new_status=AssignmentStatus.REVIEW_IN_PROGRESS, assignment_id=assignment.id),
        session,
    )

    is_pr = is_github_pull_request_url(assignment.url)
    check_note = (
        "Это ссылка на пул-реквест, так что откомментируй работу прямо на Гитхабе"
        if is_pr
        else "Это не похоже на пул-реквест, поэтому напиши ревью одним сообщением мне в ответ, я перешлю его студенту."
    )
    replay_markup = compose_curator_assignment_pull_request_check_markup() if is_pr else None

    return ActResult(
        messages=[
            f"{assignment.student.full_name} сдал работу: {assignment.url}",
            check_note,
        ],
        screenplay_id="curator.check_assignment",
        act_id="checked",
        replay_markup=replay_markup,
        context={"assignment_id": str(assignment.id)},
    )


def finished_assignment_check(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    assignment = fetch_assignment_by_id(int(context["assignment_id"]), session)
    assert assignment
    assert curator

    if message.text != "Готово":
        assignment.curator_feedback = message.text
    assignment.status = AssignmentStatus.REVIEWED
    update(assignment, session)
    create(
        AssignmentStatusHistory(new_status=AssignmentStatus.REVIEWED, assignment_id=assignment.id),
        session,
    )
    handle_assignment_checked(assignment, bot)

    next_assignment = fetch_oldest_pending_assignment_for_curator(curator.id, session=session)
    if next_assignment:
        return ActResult(
            screenplay_id="curator.check_assignment",
            act_id="check",
            context={"assignment_id": str(assignment.id)},
            play_next_act_now=True,
        )
    else:
        return ActResult(
            messages=["Все задания проверены. Хорошая работа!"],
            screenplay_id=None,
            act_id=None,
            is_screenplay_over=True,
        )
