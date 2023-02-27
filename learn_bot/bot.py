import functools
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from telebot import TeleBot

from learn_bot.config import BotConfig


class BotWithDatabaseAccessMixin:
    def __init__(self, db_engine: Engine, *args: Any, **kwargs: Any) -> None:
        self.db_engine = db_engine
        super().__init__(*args, **kwargs)

    def get_session(self) -> Session:
        return Session(self.db_engine)


class Bot(BotWithDatabaseAccessMixin, TeleBot):
    pass


def _configure_handlers(bot: TeleBot, config: BotConfig) -> None:
    from learn_bot.handlers import start_handler

    bot.message_handler(commands=["start"])(functools.partial(start_handler, bot=bot, config=config))


def compose_bot(config: BotConfig) -> Bot:
    db_engine = create_engine(config.db_dsn, echo=config.db_echo)
    bot = Bot(token=config.telegram_token, colorful_logs=True, db_engine=db_engine)

    _configure_handlers(bot, config)

    return bot
