from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig


def unknown_action_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    bot.reply_to(message, "Я не понимаю этой фразы.")
