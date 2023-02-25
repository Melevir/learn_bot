import functools

from telebot import TeleBot

from learn_bot.config import BotConfig
from learn_bot.handlers import start_handler


def _configure_handlers(bot: TeleBot, config: BotConfig) -> None:
    bot.message_handler(commands=["start"])(functools.partial(start_handler, bot=bot, config=config))


def compose_bot(config: BotConfig) -> TeleBot:
    bot = TeleBot(config.telegram_token, colorful_logs=True)

    _configure_handlers(bot, config)

    return bot
