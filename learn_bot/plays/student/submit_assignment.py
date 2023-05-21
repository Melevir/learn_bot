from typing import Mapping

from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Assignment
from learn_bot.db.changers import create
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.utils.urls import is_url_accessible, is_valid_github_url
from learn_bot.markups import compose_post_submit_assignment_markup
from learn_bot.screenplay.custom_types import ActResult
from learn_bot.screenplay.db.models.user import User
from learn_bot.services.assignment import handle_new_assignment
from learn_bot.services.student import fetch_student_from_message


def intro(user: User, context: Mapping[str, str], message: Message, bot: Bot, config: BotConfig) -> ActResult:
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
) -> ActResult:
    assignment_url = message.text
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
    with bot.get_session() as session:
        student = fetch_student_from_message(message, session)
        assert student
        assignment = Assignment(url=assignment_url, student_id=student.id, status=AssignmentStatus.READY_FOR_REVIEW)
        create(assignment, session)
        handle_new_assignment(assignment, bot)
        curator_name = student.group.curator.first_name
    return ActResult(
        screenplay_id=context["screenplay_id"],
        act_id="one_more_assignment",
        messages=[
            (
                f"Записал! Дам знать, как {curator_name} проверит твою работу. "
                f"Хочешь сдать ещё одну?"
            ),
        ],
        replay_markup=compose_post_submit_assignment_markup(),
    )


def one_more_assignment(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
) -> ActResult:
    if message.text == "Да, сдам ещё одну":
        return ActResult(screenplay_id=context["screenplay_id"], act_id="create_assignment", play_next_act_now=True)
    else:
        return ActResult(messages=["Тогда до скорого"], screenplay_id=None, act_id=None, is_screenplay_over=True)
