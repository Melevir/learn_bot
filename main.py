from typing import NoReturn

from telebot import TeleBot

from learn_bot.bot import compose_bot
from learn_bot.commands_manager.argparser import compose_command_argparser
from learn_bot.commands_manager.runner import run_command
from learn_bot.config import get_config
from learn_bot.logs import configure_logging
from learn_bot.sentry import configure_sentry


def run_bot(bot: TeleBot) -> NoReturn:
    bot.infinity_polling(restart_on_change=True)


if __name__ == "__main__":
    config = get_config()

    configure_logging()
    configure_sentry(config.sentry_dsn)

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
