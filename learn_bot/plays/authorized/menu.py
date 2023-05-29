from typing import Mapping

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Curator, Student
from learn_bot.message_composers import compose_available_commands_message
from learn_bot.screenplay.custom_types import ActResult
from learn_bot.screenplay.db.changers import update_active_act_for
from learn_bot.screenplay.db.models.user import User


def show(
    user: User,
    context: Mapping[str, str],
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
    curator: Curator | None,
    student: Student | None,
) -> ActResult:
    update_active_act_for(user.id, None, None, session)
    message_text = compose_available_commands_message(user, bot)
    return ActResult(messages=[message_text], is_screenplay_over=True)
