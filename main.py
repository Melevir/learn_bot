from telebot import TeleBot

from learn_bot.bot import compose_bot
from learn_bot.commands_manager.argparser import compose_command_argparser
from learn_bot.commands_manager.runner import run_command
from learn_bot.config import BotConfig, get_config
from learn_bot.logs import configure_logging
from learn_bot.sentry import configure_sentry


def run_bot(bot: TeleBot, config: BotConfig) -> None:
    bot.infinity_polling(restart_on_change=config.restart_on_change)


if __name__ == "__main__":
    config = get_config()

    configure_logging()
    if config.sentry_dsn:
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
        run_bot(bot, config)
