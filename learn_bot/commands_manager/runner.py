import importlib
import logging

from learn_bot.bot import Bot
from learn_bot.config import BotConfig

logger = logging.getLogger(__name__)


def run_command(
    bot: Bot,
    config: BotConfig,
    command_name: str,
    commands_module: str,
    callable_name: str = "run",
) -> None:
    command_importable_path = f"{commands_module}.{command_name}"
    logger.info(f"Running command {command_name} from module {command_importable_path}")
    try:
        command_module = importlib.import_module(command_importable_path)
    except ModuleNotFoundError:
        logger.error(f"Module {command_importable_path} not found")
        return
    try:
        command_callable = getattr(command_module, callable_name)
    except AttributeError:
        logger.error(f"Module {command_importable_path} has no attribute {callable_name}")
        return

    command_callable(bot=bot, config=config)
