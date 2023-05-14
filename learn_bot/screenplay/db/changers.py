from typing import Mapping

from sqlalchemy import update, delete
from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.db.changers import create
from learn_bot.screenplay.db.fetchers import fetch_screenplay_context, fetch_user_by_telegram_nickname
from learn_bot.screenplay.db.models.screenplay_context import ScreenplayContext
from learn_bot.screenplay.db.models.user import User


def update_active_act_for(user_id: int, screenplay_id: str, act_id: str, session: Session) -> None:
    session.execute(
        update(User).where(User.id == user_id).values(
            active_screenplay_id=screenplay_id,
            active_act_id=act_id,
        )
    )
    session.commit()


def update_screenplay_context(
    new_context: Mapping[str, str],
    user_id: int,
    screenplay_id: str,
    session: Session,
) -> None:
    if context := fetch_screenplay_context(user_id, screenplay_id, session):
        context |= new_context
        session.execute(
            update(ScreenplayContext).where(
                ScreenplayContext.user_id == user_id,
                ScreenplayContext.screenplay_id == screenplay_id,
            ).values(
                data=context
            )
        )
        session.commit()
    else:
        create(
            ScreenplayContext(
                user_id=user_id,
                screenplay_id=screenplay_id,
                data=new_context,
            ),
            session
        )

def clean_screenplay_context(user_id: int, screenplay_id: str, session: Session) -> None:
    session.execute(
        delete(ScreenplayContext).where(
            ScreenplayContext.user_id == user_id,
            ScreenplayContext.screenplay_id == screenplay_id,
        )
    )
    session.commit()


def get_or_create_user_from(
    message: Message,
    session: Session,
    active_screenplay_id: str,
    active_act_id: str,
) -> User:
    if user := fetch_user_by_telegram_nickname(message.from_user.username, session):
        return user
    user = User(
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        telegram_nickname=message.from_user.username,
        telegram_chat_id=str(message.chat.id),
        active_screenplay_id=active_screenplay_id,
        active_act_id=active_act_id,
    )
    create(user, session)
    return user
