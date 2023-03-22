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
        from learn_bot.plays.curator.check_assignment import (
            list_pending_assignments, start_assignments_check, check_oldest_pending_assignment,
            finished_assignment_check,
        )

        handlers_map = {
            "student.submit_assignment": {
                "intro": intro,
                "create_assignment": create_assignment,
                "one_more_assignment": one_more_assignment,
            },
            "curator.check_assignment": {
                "list": list_pending_assignments,
                "start": start_assignments_check,
                "check": check_oldest_pending_assignment,
                "checked": finished_assignment_check,
            }
        }
        return handlers_map[screenplay_id][act_id]
