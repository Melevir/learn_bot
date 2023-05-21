import dataclasses
from typing import Mapping, Callable

from telebot.types import ReplyKeyboardMarkup, Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.screenplay.db.models.user import User


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ActResult:
    screenplay_id: str | None
    act_id: str | None
    messages: list[str] | None = None
    replay_markup: ReplyKeyboardMarkup | None = None
    context: Mapping[str, str] | None = None
    is_screenplay_over: bool = False
    play_next_act_now: bool = False


PlayHandler = Callable[[User, Mapping[str, str], Message, Bot, BotConfig], ActResult]


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ScreenPlay:
    name: str
    acts: list[tuple[str, PlayHandler]]
    allowed_for_roles: list[str]
    short_description: str
    command_to_start: str | None = None
