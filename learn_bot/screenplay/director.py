from __future__ import annotations
from typing import Callable, Mapping, TYPE_CHECKING

from telebot.types import Message

from learn_bot.config import BotConfig
from learn_bot.screenplay.custom_types import ActResult
if TYPE_CHECKING:
    from learn_bot.screenplay.db.models.user import User
    from learn_bot.bot import Bot


class ScreenplayDirector:
    def fetch_act_handler(
        self,
        screenplay_id: str,
        act_id: str,
    ) -> Callable[[User, Mapping[str, str], Message, Bot, BotConfig], ActResult]:
        from learn_bot.plays.student.submit_assignment import intro, create_assignment, one_more_assignment

        handlers_map = {
            "student.submit_assignment": {
                "intro": intro,
                "create_assignment": create_assignment,
                "one_more_assignment": one_more_assignment,
            }
        }
        return handlers_map[screenplay_id][act_id]
