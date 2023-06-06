import dataclasses
from typing import Callable, Mapping, Sequence

from sqlalchemy.orm import Session
from telebot.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Curator, Student
from learn_bot.db.enums import UserRole
from learn_bot.screenplay.db.models.user import User


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class TelegramMessageDescription:
    text: str
    reply_to_message_id: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ActResult:
    screenplay_id: str | None = None
    act_id: str | None = None
    messages: Sequence[str | TelegramMessageDescription] | None = None
    replay_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None
    context: Mapping[str, str] | None = None
    is_screenplay_over: bool = False
    play_next_act_now: bool = False


PlayHandler = Callable[
    [User, Mapping[str, str], Message, Bot, BotConfig, Session, Curator | None, Student | None],
    ActResult,
]


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ScreenPlay:
    name: str
    acts: list[tuple[str, PlayHandler]]
    allowed_for_roles: set[UserRole]
    short_description: str
    command_to_start: str | None = None
    is_hidden_from_commands_list: bool = False
