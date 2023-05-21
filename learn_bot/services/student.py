from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.db import Student
from learn_bot.db.fetchers import fetch_student_by_chat_id, fetch_student_by_telegram_nickname


def fetch_student_from_message(message: Message, session: Session) -> Student | None:
    return (
        fetch_student_by_telegram_nickname(message.from_user.username, session)
        or fetch_student_by_chat_id(message.chat.id, session)
    )
