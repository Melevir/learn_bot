from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_bot.screenplay.db.models.screenplay_context import ScreenplayContext
from learn_bot.screenplay.db.models.screenplay_request import ScreenplayRequest
from learn_bot.screenplay.db.models.user import User


def fetch_user_by_chat_id(chat_id: str | None, session: Session) -> User | None:
    if not chat_id:
        return None
    return session.scalar(
        select(User).where(
            User.telegram_chat_id == str(chat_id),
        ),
    )


def fetch_user_by_telegram_nickname(nickname: str | None, session: Session) -> User | None:
    if nickname is None:
        return None
    return session.scalar(
        select(User).where(
            User.telegram_nickname == nickname.lower(),
        ),
    )


def fetch_user_by_user_id(user_id: int, session: Session) -> User | None:
    return session.scalar(
        select(User).where(
            User.id == user_id,
        ),
    )


def fetch_active_act_for(user_id: int, session: Session) -> tuple[str | None, str | None]:
    user = fetch_user_by_user_id(user_id, session)
    if not user:
        return None, None
    return user.active_screenplay_id, user.active_act_id


def fetch_screenplay_context(user_id: int, screenplay_id: str, session: Session) -> dict[str, str]:
    context_object = session.scalar(
        select(ScreenplayContext).where(
            ScreenplayContext.user_id == user_id,
            ScreenplayContext.screenplay_id == screenplay_id,
        ),
    )
    return context_object.data if context_object else {}


def fetch_screenplay_request(
    screenplay_id: str,
    act_id: str,
    encoded_context: str,
    session: Session,
) -> ScreenplayRequest | None:
    return session.scalar(
        select(ScreenplayRequest).where(
            ScreenplayRequest.screenplay_id == screenplay_id,
            ScreenplayRequest.act_id == act_id,
            ScreenplayRequest.context == encoded_context,
        ),
    )


def fetch_screenplay_request_by_id(
    screenplay_request_id: int,
    session: Session,
) -> ScreenplayRequest | None:
    return session.scalar(
        select(ScreenplayRequest).where(
            ScreenplayRequest.id == screenplay_request_id,
        ),
    )
