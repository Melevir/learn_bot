import functools
from typing import Any

import sentry_sdk
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from telebot import TeleBot

from learn_bot.config import BotConfig
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


def compose_bot(config: BotConfig) -> Bot:
    db_engine = create_engine(config.db_dsn, echo=config.db_echo)
    bot = Bot(
        token=config.telegram_token,
        colorful_logs=True,
        exception_handler=SentryExceptionHandler(),
        threaded=False,

        db_engine=db_engine,
        screenplay_director=ScreenplayDirector()
    )

    _configure_handlers(bot, config)

    return bot
