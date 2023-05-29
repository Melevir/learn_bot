import json

from sqlalchemy.orm import Session
from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.screenplay.db.changers import update_active_act_for, update_screenplay_context
from learn_bot.screenplay.db.models.screenplay_request import ScreenplayRequest
from learn_bot.screenplay.db.models.user import User
from learn_bot.screenplay.default_handlers import unknown_action_handler
from learn_bot.screenplay.services.play_act import play_active_act_for


def process_play_request(
    play_request: ScreenplayRequest,
    user: User,
    message: Message,
    bot: Bot,
    config: BotConfig,
    session: Session,
) -> None:
    play = bot.screenplay_director.get_play_by_name(play_request.screenplay_id)
    with bot.get_session() as session:
        role = bot.role_provider(user, session)
    if play is None or role not in play.allowed_for_roles:
        unknown_action_handler(message, bot, config)
        return
    play_context = json.loads(play_request.context)
    with bot.get_session() as session:
        update_active_act_for(user.id, play_request.screenplay_id, play_request.act_id, session)
        update_screenplay_context(play_context, user.id, play_request.screenplay_id, session)
    play_active_act_for(user, message, bot, config)
