from typing import Mapping

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Curator, Student
from learn_bot.db.changers import update
from learn_bot.db.fetchers import fetch_not_connected_student_by_auth_code, fetch_student_by_id
from learn_bot.message_composers import compose_available_commands_message
from learn_bot.screenplay.custom_types import ActResult
from learn_bot.screenplay.db.changers import get_or_create_user_from
from learn_bot.screenplay.db.models.user import User


def start(
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
        act_id="process_code",
        messages=[
            "Если у тебя есть авторизационный код, скажи его мне",
            "Пожалуйста не пиши ничего, кроме кода",
        ],
    )


def process_code(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    auth_code = message.text.strip().lower()
    student = fetch_not_connected_student_by_auth_code(auth_code, session)
    next_act_id = "code_is_correct" if student is not None else "code_is_incorrect"
    return ActResult(
        screenplay_id=context["screenplay_id"],
        act_id=next_act_id,
        context={"student_id": str(student.id)} if student else None,
        play_next_act_now=True,
    )


def code_is_correct(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    student = fetch_student_by_id(int(context["student_id"]), session)
    if not student:
        return ActResult(
            screenplay_id=context["screenplay_id"],
            act_id="code_is_incorrect",
            play_next_act_now=True,
        )

    student.telegram_nickname = message.from_user.username
    student.telegram_chat_id = message.chat.id
    update(student, session)
    user = get_or_create_user_from(message, session)

    curator = student.group.curator
    return ActResult(
        screenplay_id=None,
        act_id=None,
        is_screenplay_over=True,
        messages=[
            f"Привет, {student.first_name}. Твой куратор {curator.full_name} (@{curator.telegram_nickname})",
            compose_available_commands_message(user, bot),
        ],
    )


def code_is_incorrect(
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
        screenplay_id=None,
        act_id=None,
        is_screenplay_over=True,
        messages=["Код неверный"],
    )
