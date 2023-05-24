from typing import Mapping

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Curator, Student
from learn_bot.screenplay.custom_types import ActResult
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
        screenplay_id=None,
        act_id=None,
        is_screenplay_over=True,
        messages=[],
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
    return ActResult(
        screenplay_id=None,
        act_id=None,
        is_screenplay_over=True,
        messages=[],
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
    return ActResult(
        screenplay_id=None,
        act_id=None,
        is_screenplay_over=True,
        messages=[],
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
        messages=[],
    )
