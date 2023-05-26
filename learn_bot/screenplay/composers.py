import json

from sqlalchemy.orm import Session
from telebot.types import CallbackQuery

from learn_bot.screenplay.custom_types import ScreenPlayRequest
from learn_bot.screenplay.db.fetchers import fetch_user_by_chat_id


def compose_play_request_from(call: CallbackQuery, session: Session) -> ScreenPlayRequest:
    raw_call_data = json.loads(call.data)

    user = fetch_user_by_chat_id(str(call.message.chat.id), session)
    assert user

    return ScreenPlayRequest(
        user_id=user.id,
        screenplay_id=raw_call_data["screenplay_id"],
        act_id=raw_call_data.get("act_id"),
        context=raw_call_data.get("context", {}),
    )
