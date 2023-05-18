import logging

from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.screenplay.db.changers import get_or_create_user_from, update_active_act_for, save_message_to_db
from learn_bot.screenplay.db.fetchers import fetch_user_by_chat_id
from learn_bot.screenplay.default_handlers import unknown_action_handler
from learn_bot.screenplay.services.play_act import play_active_act_for


logger = logging.getLogger(__name__)


def message_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    if message.chat.type != "private":
        return

    with bot.get_session() as session:
        save_message_to_db(message, session)
        user = fetch_user_by_chat_id(message.chat.id, session)
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
            if user.active_screenplay_id:
                play_active_act_for(user, message, bot, config)
            else:
                with bot.get_session() as session:
                    role = bot.role_provider(user, session)
                if role is None:
                    bot.send_message(message.chat.id, "Кажется, мы с вами не знакомы.")
                    return
                allowed_plays = [p for p in bot.screenplay_director.fetch_plays_for_role(role) if p.command_to_start]
                allowed_commands_lines = '\n'.join([
                    f"- /{p.command_to_start} – {p.short_description}"
                    for p in allowed_plays
                ])
                message_text = f"Вам доступны следующие команды:\n{allowed_commands_lines}"
                bot.send_message(message.chat.id, message_text)
    else:
        with bot.get_session() as session:
            user = fetch_user_by_chat_id(message.chat.id, session)
        play = bot.screenplay_director.get_play_for_command(command)
        with bot.get_session() as session:
            role = bot.role_provider(user, session)
        if play is None or role not in play.allowed_for_roles:
            unknown_action_handler(message, bot, config)
            return
        with bot.get_session() as session:
            update_active_act_for(user.id, play.name, play.acts[0][0], session)
        play_active_act_for(user, message, bot, config)
