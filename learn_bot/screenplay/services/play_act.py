from telebot.types import Message, ReplyKeyboardRemove

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db.changers import update_contacts
from learn_bot.screenplay.custom_types import ActResult, TelegramMessageDescription
from learn_bot.screenplay.db.changers import clean_screenplay_context, update_active_act_for, update_screenplay_context
from learn_bot.screenplay.db.fetchers import fetch_active_act_for, fetch_screenplay_context
from learn_bot.screenplay.db.models.user import User
from learn_bot.screenplay.default_handlers import unknown_action_handler
from learn_bot.services.curator import fetch_curator_from_message
from learn_bot.services.student import fetch_student_from_message


def play_active_act_for(user: User, message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        screenplay_id, act_id = fetch_active_act_for(user.id, session)
        if screenplay_id is None or act_id is None:
            return unknown_action_handler(message, bot, config)
        screenplay_context = fetch_screenplay_context(user.id, screenplay_id, session)
    screenplay_context |= {
        "screenplay_id": screenplay_id,
        "act_id": act_id,
    }
    act_handler = bot.screenplay_director.fetch_act_handler(screenplay_id, act_id)
    with bot.get_session() as session:
        curator = fetch_curator_from_message(message, session)
        student = fetch_student_from_message(message, session)
        if curator:
            update_contacts(curator, message, session)
        if student:
            update_contacts(student, message, session)

        act_result = act_handler(
            user,
            screenplay_context,
            message,
            bot,
            config,
            session,
            curator,
            student,
        )
        update_active_act_for(user.id, act_result.screenplay_id, act_result.act_id, session)
    _handle_act_result(act_result, user, message, bot, config, screenplay_id)


def _handle_act_result(
    act_result: ActResult,
    user: User,
    message: Message,
    bot: Bot,
    config: BotConfig,
    screenplay_id: str,
) -> None:
    if act_result.messages:
        for message_description in act_result.messages:
            message_text = None
            reply_to_message_id = None
            if isinstance(message_description, str):
                message_text = message_description
            elif isinstance(message_description, TelegramMessageDescription):
                message_text = message_description.text
                reply_to_message_id = message_description.reply_to_message_id
            assert message_text

            bot.send_message(
                message.chat.id,
                message_text,
                reply_markup=act_result.replay_markup or ReplyKeyboardRemove(),
                reply_to_message_id=reply_to_message_id,
            )
    with bot.get_session() as session:
        if act_result.context:
            update_screenplay_context(act_result.context, user.id, screenplay_id, session)
        if act_result.is_screenplay_over:
            clean_screenplay_context(user.id, screenplay_id, session)
    if act_result.play_next_act_now and act_result.screenplay_id and act_result.act_id:
        play_active_act_for(user, message, bot, config)
