import dataclasses
from typing import Mapping

from telebot.types import ReplyKeyboardMarkup


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ActResult:
    screenplay_id: str | None
    act_id: str | None
    messages: list[str] | None = None
    replay_markup: ReplyKeyboardMarkup | None = None
    context: Mapping[str, str] | None = None
    is_screenplay_over: bool = False
    play_next_act_now: bool = False
