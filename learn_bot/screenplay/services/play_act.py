from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.screenplay.db.changers import update_active_act_for, update_screenplay_context, clean_screenplay_context
from learn_bot.screenplay.db.fetchers import fetch_active_act_for, fetch_screenplay_context
from learn_bot.screenplay.db.models.user import User
from learn_bot.screenplay.default_handlers import unknown_action_handler


def play_active_act_for(user: User, message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        screenplay_id, act_id = fetch_active_act_for(user.id, session)
        if screenplay_id is None:
            return unknown_action_handler(message, bot, config)
        screenplay_context = fetch_screenplay_context(user.id, screenplay_id, session)
    screenplay_context |= {
        "screenplay_id": screenplay_id,
        "act_id": act_id,
    }
    act_handler = bot.screenplay_director.fetch_act_handler(screenplay_id, act_id)
    act_result = act_handler(user, screenplay_context, message, bot, config)
    with bot.get_session() as session:
        update_active_act_for(user.id, act_result.screenplay_id, act_result.act_id, session)
    if act_result.messages:
        for message_text in act_result.messages:
            bot.send_message(
                message.chat.id,
                message_text,
                reply_markup=act_result.replay_markup,
            )
    with bot.get_session() as session:
        if act_result.context:
            update_screenplay_context(act_result.context, user.id, screenplay_id, session)
        if act_result.is_screenplay_over:
            clean_screenplay_context(user.id, screenplay_id, session)
    if act_result.play_next_act_now and act_result.screenplay_id and act_result.act_id:
        play_active_act_for(user, message, bot, config)
