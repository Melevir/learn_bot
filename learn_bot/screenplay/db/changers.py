import json
from typing import Mapping, cast

from sqlalchemy import delete, update
from sqlalchemy.orm import Session
from telebot.types import CallbackQuery, Message

from learn_bot.db.changers import create
from learn_bot.screenplay.db.fetchers import (
    fetch_screenplay_context,
    fetch_screenplay_request,
    fetch_user_by_chat_id,
    fetch_user_by_telegram_nickname,
)
from learn_bot.screenplay.db.models.message import ChatMessage
from learn_bot.screenplay.db.models.screenplay_context import ScreenplayContext
from learn_bot.screenplay.db.models.screenplay_request import ScreenplayRequest
from learn_bot.screenplay.db.models.user import User


def update_active_act_for(user_id: int, screenplay_id: str | None, act_id: str | None, session: Session) -> None:
    session.execute(
        update(User).where(User.id == user_id).values(
            active_screenplay_id=screenplay_id,
            active_act_id=act_id,
        ),
    )
    session.commit()


def update_screenplay_context(
    new_context: Mapping[str, str],
    user_id: int,
    screenplay_id: str,
    session: Session,
) -> None:
    if context := fetch_screenplay_context(user_id, screenplay_id, session):
        print(f"{context=}")
        print(f"{new_context=}")
        context |= new_context
        session.execute(
            update(ScreenplayContext).where(
                ScreenplayContext.user_id == user_id,
                ScreenplayContext.screenplay_id == screenplay_id,
            ).values(
                data=context,
            ),
        )
        session.commit()
    else:
        create(
            ScreenplayContext(
                user_id=user_id,
                screenplay_id=screenplay_id,
                data=new_context,
            ),
            session,
        )


def clean_screenplay_context(user_id: int, screenplay_id: str, session: Session) -> None:
    session.execute(
        delete(ScreenplayContext).where(
            ScreenplayContext.user_id == user_id,
            ScreenplayContext.screenplay_id == screenplay_id,
        ),
    )
    session.commit()


def get_or_create_user_from(
    message: Message,
    session: Session,
    active_screenplay_id: str | None = None,
    active_act_id: str | None = None,
) -> User:
    if message.from_user.username:
        if user := fetch_user_by_telegram_nickname(message.from_user.username, session):
            return user
    if user := fetch_user_by_chat_id(str(message.chat.id), session):
        return user
    user = User(
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        telegram_nickname=message.from_user.username.lower() if message.from_user.username else None,
        telegram_chat_id=str(message.chat.id),
        active_screenplay_id=active_screenplay_id,
        active_act_id=active_act_id,
    )
    create(user, session)
    return user


def save_message_to_db(message: Message, session: Session) -> ChatMessage:
    chat_message = ChatMessage(
        telegram_chat_id=message.chat.id,
        from_user_id=message.from_user.id,
        message=message.text,
    )
    create(chat_message, session)
    return chat_message


def save_callback_query_to_db(call: CallbackQuery, session: Session) -> ChatMessage:
    chat_message = ChatMessage(
        telegram_chat_id=call.message.chat.id,
        from_user_id=call.from_user.id,
        message=f"Callback query with data: {call.data}",
    )
    create(chat_message, session)
    return chat_message


def get_or_create_screenplay_request(
    screenplay_id: str,
    act_id: str,
    context: Mapping[str, str] | None,
    session: Session,
) -> ScreenplayRequest:
    encoded_context = json.dumps(context or {})
    if request := fetch_screenplay_request(screenplay_id, act_id, encoded_context, session):
        return request
    return cast(
        ScreenplayRequest,
        create(
            ScreenplayRequest(
                screenplay_id=screenplay_id,
                act_id=act_id,
                context=encoded_context,
            ),
            session,
        ),
    )
