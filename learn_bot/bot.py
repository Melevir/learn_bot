from __future__ import annotations
import functools
from typing import Any, TYPE_CHECKING

import sentry_sdk
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from telebot import TeleBot

from learn_bot.config import BotConfig

if TYPE_CHECKING:
    from learn_bot.screenplay.director import ScreenplayDirector


class BotWithDatabaseAccessMixin:
    def __init__(self, db_engine: Engine, *args: Any, **kwargs: Any) -> None:
        self.db_engine = db_engine
        super().__init__(*args, **kwargs)

    def get_session(self) -> Session:
        return Session(self.db_engine)


class BotWithScreenplayDirectorMixin:
    def __init__(self, screenplay_director: ScreenplayDirector, *args: Any, **kwargs: Any) -> None:
        self.screenplay_director = screenplay_director
        super().__init__(*args, **kwargs)


class Bot(BotWithDatabaseAccessMixin, BotWithScreenplayDirectorMixin, TeleBot):
    pass


class SentryExceptionHandler:
    def handle(self, exception):
        return sentry_sdk.capture_exception(exception)


def _configure_handlers(bot: TeleBot, config: BotConfig) -> None:
    from learn_bot.handlers import start_handler, message_handler

    bot.register_message_handler(
        functools.partial(start_handler, bot=bot, config=config),
        commands=["start"],
    )
    bot.register_message_handler(
        functools.partial(message_handler, bot=bot, config=config),
    )


def _compose_screenplay_director() -> ScreenplayDirector:
    from learn_bot.screenplay.custom_types import ScreenPlay
    from learn_bot.screenplay.director import ScreenplayDirector
    from learn_bot.plays.curator.check_assignment import (
        list_pending_assignments, start_assignments_check, check_oldest_pending_assignment, finished_assignment_check,
    )
    from learn_bot.plays.student.submit_assignment import intro, create_assignment, one_more_assignment

    director = ScreenplayDirector()
    director.register_play(
        ScreenPlay(
            name="student.submit_assignment",
            acts=[
                ("intro", intro),
                ("create_assignment", create_assignment),
                ("one_more_assignment", one_more_assignment),
            ],
        ),
    )
    director.register_play(
        ScreenPlay(
            name="curator.check_assignment",
            acts=[
                ("list", list_pending_assignments),
                ("start", start_assignments_check),
                ("check", check_oldest_pending_assignment),
                ("checked", finished_assignment_check),
            ],
        ),
    )
    return director


def compose_bot(config: BotConfig) -> Bot:
    db_engine = create_engine(config.db_dsn, echo=config.db_echo)

    director = _compose_screenplay_director()

    bot = Bot(
        token=config.telegram_token,
        colorful_logs=True,
        exception_handler=SentryExceptionHandler(),
        threaded=False,

        db_engine=db_engine,
        screenplay_director=director,
    )

    _configure_handlers(bot, config)

    return bot
