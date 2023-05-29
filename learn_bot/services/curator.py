from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.db import Curator
from learn_bot.db.fetchers import fetch_curator_by_chat_id, fetch_curator_by_telegram_nickname


def fetch_curator_from_message(message: Message, session: Session) -> Curator | None:
    return (
        fetch_curator_by_chat_id(str(message.chat.id), session)
        or fetch_curator_by_telegram_nickname(message.from_user.username, session)
    )
