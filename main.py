from typing import NoReturn

from telebot import TeleBot

from learn_bot.bot import compose_bot
from learn_bot.config import get_config
from learn_bot.logs import configure_logging


def run_bot(bot: TeleBot) -> NoReturn:
    bot.infinity_polling()


if __name__ == "__main__":
    configure_logging()
    config = get_config()
    bot = compose_bot(config)
    run_bot(bot)
