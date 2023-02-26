from typing import NoReturn

from telebot import TeleBot

from learn_bot.bot import compose_bot
from learn_bot.commands_manager.argparser import compose_command_argparser
from learn_bot.commands_manager.runner import run_command
from learn_bot.config import get_config
from learn_bot.logs import configure_logging


def run_bot(bot: TeleBot) -> NoReturn:
    bot.infinity_polling()


if __name__ == "__main__":
    configure_logging()
    config = get_config()
    bot = compose_bot(config)
    args = compose_command_argparser().parse_args()
    if args.command:
        run_command(
            bot,
            config,
            args.command,
            commands_module="learn_bot.commands",
        )
    else:
        run_bot(bot)
