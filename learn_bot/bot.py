from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable

import sentry_sdk
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from telebot import REPLY_MARKUP_TYPES, TeleBot
from telebot.types import Message, MessageEntity

from learn_bot.config import BotConfig
from learn_bot.db.changers import create
from learn_bot.db.enums import UserRole
from learn_bot.db.fetchers import fetch_role_by_user
from learn_bot.screenplay.db.models.message import ChatMessage
from learn_bot.screenplay.db.models.user import User

if TYPE_CHECKING:
    from learn_bot.screenplay.director import ScreenplayDirector


class BotWithDatabaseAccessMixin:
    save_responses_to_db = True

    def __init__(
        self,
        db_engine: Engine,
        role_provider: Callable[[User, Session], UserRole],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.db_engine = db_engine
        self.role_provider = role_provider
        super().__init__(*args, **kwargs)

    def get_session(self) -> Session:
        return Session(self.db_engine)

    def send_message(  # noqa: CFQ002
            self,
            chat_id: int | str,
            text: str,
            parse_mode: str | None = None,
            entities: list[MessageEntity] | None = None,
            disable_web_page_preview: bool = True,
            disable_notification: bool | None = None,
            protect_content: bool | None = None,
            reply_to_message_id: int | None = None,
            allow_sending_without_reply: bool | None = None,
            reply_markup: REPLY_MARKUP_TYPES | None = None,
            timeout: int | None = None,
            message_thread_id: int | None = None,
    ) -> Message:
        if self.save_responses_to_db:
            with self.get_session() as session:
                create(
                    ChatMessage(
                        telegram_chat_id=chat_id,
                        from_user_id=self.user.id,  # type: ignore[attr-defined]
                        message=text,
                    ),
                    session,
                )

        return super().send_message(  # type: ignore[misc]
            chat_id,
            text,
            parse_mode,
            entities,
            disable_web_page_preview,
            disable_notification,
            protect_content,
            reply_to_message_id,
            allow_sending_without_reply,
            reply_markup,
            timeout,
            message_thread_id,
        )


class BotWithScreenplayDirectorMixin:
    def __init__(self, screenplay_director: ScreenplayDirector, *args: Any, **kwargs: Any) -> None:
        self.screenplay_director = screenplay_director
        super().__init__(*args, **kwargs)


class Bot(BotWithDatabaseAccessMixin, BotWithScreenplayDirectorMixin, TeleBot):
    pass


class SentryExceptionHandler:
    def handle(self, exception: Exception) -> None:
        sentry_sdk.capture_exception(exception)


def _configure_handlers(bot: Bot, config: BotConfig) -> None:
    from learn_bot.handlers import command_handler, message_handler

    bot.register_message_handler(
        functools.partial(command_handler, bot=bot, config=config),
        commands=["start"] + bot.screenplay_director.get_all_commands(),
    )
    bot.register_message_handler(
        functools.partial(message_handler, bot=bot, config=config),
    )


def _compose_screenplay_director() -> ScreenplayDirector:
    from learn_bot.plays.curator.check_assignment import (
        check_oldest_pending_assignment,
        finished_assignment_check,
        list_pending_assignments,
        start_assignments_check,
    )
    from learn_bot.plays.curator.weekly_student_report import show_weekly_students_report
    from learn_bot.plays.student.submit_assignment import create_assignment, intro
    from learn_bot.screenplay.custom_types import ScreenPlay
    from learn_bot.screenplay.director import ScreenplayDirector

    director = ScreenplayDirector()
    director.register_play(
        ScreenPlay(
            name="student.submit_assignment",
            short_description="сдать работу на проверку",
            acts=[
                ("intro", intro),
                ("create_assignment", create_assignment),
            ],
            allowed_for_roles={UserRole.STUDENT},
            command_to_start="submit",
        ),
    )
    director.register_play(
        ScreenPlay(
            name="curator.check_assignment",
            short_description="проверить работы",
            acts=[
                ("list", list_pending_assignments),
                ("start", start_assignments_check),
                ("check", check_oldest_pending_assignment),
                ("checked", finished_assignment_check),
            ],
            allowed_for_roles={UserRole.CURATOR},
            command_to_start="check",
        ),
    )
    director.register_play(
        ScreenPlay(
            name="curator.weekly_student_report",
            short_description="показать отчёт по сданным работам",
            acts=[
                ("show", show_weekly_students_report),
            ],
            allowed_for_roles={UserRole.CURATOR},
            command_to_start="assignments_report",
        ),
    )

    return director


def compose_bot(config: BotConfig) -> Bot:
    db_engine = create_engine(config.db_dsn, echo=config.db_echo)

    director = _compose_screenplay_director()

    bot = Bot(
        token=config.telegram_token,
        colorful_logs=True,
        exception_handler=SentryExceptionHandler(),
        threaded=False,

        db_engine=db_engine,
        screenplay_director=director,
        role_provider=fetch_role_by_user,
    )

    _configure_handlers(bot, config)

    return bot
