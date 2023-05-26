from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.screenplay.custom_types import ScreenPlayRequest
from learn_bot.screenplay.db.models.user import User


def process_play_request(
    play_request: ScreenPlayRequest,
    user: User,
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
) -> None:
    pass
