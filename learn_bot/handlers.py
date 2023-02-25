import logging

from telebot import TeleBot
from telebot.types import Message

from learn_bot.config import BotConfig

logger = logging.getLogger(__name__)


def start_handler(message: Message, bot: TeleBot, config: BotConfig):
    logger.info("Start called")
    msg = bot.reply_to(message, "Hi")
