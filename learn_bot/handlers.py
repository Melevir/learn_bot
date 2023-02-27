import functools
import logging

from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db.changers import update
from learn_bot.db.fetchers import fetch_curator_by_telegram_nickname, fetch_student_by_telegram_nickname
from learn_bot.markups import compose_curator_menu_markup

logger = logging.getLogger(__name__)


def start_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        curator = fetch_curator_by_telegram_nickname(message.from_user.username, session)
        student = fetch_student_by_telegram_nickname(message.from_user.username, session)

        if curator is not None:
            active_groups = [g for g in curator.groups if g.enrollment.is_active]
            active_groups_num = len(active_groups)
            groups_word = "группа" if active_groups_num == 1 else "группы"
            curator.telegram_chat_id = message.chat.id
            update(curator, session)
            reply_text = f"Привет, {curator.first_name}. У тебя {len(active_groups)} {groups_word}."
            bot.register_next_step_handler(
                message,
                functools.partial(list_pending_assignments_handle, bot=bot, config=config),
            )
            bot.reply_to(
                message,
                reply_text,
                reply_markup=compose_curator_menu_markup(),
            )


def list_pending_assignments_handle(message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        curator = fetch_curator_by_telegram_nickname(message.from_user.username, session)
        if curator is None:
            return

        assignments = []
        reply_text = f"У тебя {len(assignments) or 'нет'} заданий на проверку"
        bot.reply_to(message, reply_text)
