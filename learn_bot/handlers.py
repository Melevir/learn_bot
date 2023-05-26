import logging

from telebot.types import CallbackQuery, Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.message_composers import compose_available_commands_message
from learn_bot.screenplay.composers import compose_play_request_from
from learn_bot.screenplay.db.changers import (
    get_or_create_user_from,
    save_callback_query_to_db,
    save_message_to_db,
    update_active_act_for,
)
from learn_bot.screenplay.db.fetchers import fetch_user_by_chat_id
from learn_bot.screenplay.default_handlers import unknown_action_handler
from learn_bot.screenplay.services.play_act import play_active_act_for
from learn_bot.screenplay.services.play_request import process_play_request

logger = logging.getLogger(__name__)


def message_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    if message.chat.type != "private":
        return

    with bot.get_session() as session:
        save_message_to_db(message, session)
        user = fetch_user_by_chat_id(str(message.chat.id), session)
    if user is None:
        bot.send_message(message.chat.id, "Кажется, мы незнакомы. Пожалуйста, скажи мне /start")
        return
    play_active_act_for(user, message, bot, config)


def command_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    if message.chat.type != "private":
        return

    with bot.get_session() as session:
        save_message_to_db(message, session)

    command = message.text.lstrip("/")
    if command == "start":
        with bot.get_session() as session:
            user = get_or_create_user_from(
                message,
                session,
            )
            update_active_act_for(user.id, None, None, session)
            message_text = compose_available_commands_message(user, bot)
            bot.send_message(message.chat.id, message_text)
    else:
        with bot.get_session() as session:
            command_user = fetch_user_by_chat_id(str(message.chat.id), session)
            assert command_user
            user = command_user
        play = bot.screenplay_director.get_play_for_command(command)
        with bot.get_session() as session:
            role = bot.role_provider(user, session)
        if play is None or role not in play.allowed_for_roles:
            unknown_action_handler(message, bot, config)
            return
        with bot.get_session() as session:
            update_active_act_for(user.id, play.name, play.acts[0][0], session)
        play_active_act_for(user, message, bot, config)


def callback_query_handler(call: CallbackQuery, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        play_request = compose_play_request_from(call, session)
        save_callback_query_to_db(call, session)
        user = fetch_user_by_chat_id(str(call.message.chat.id), session)
        assert user

        process_play_request(play_request, user, call.message, bot, config, session)
