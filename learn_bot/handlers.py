import functools
import logging

from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Assignment
from learn_bot.db.changers import update, create
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.fetchers import fetch_curator_by_telegram_nickname, fetch_student_by_telegram_nickname, \
    fetch_assignments_for_curator, fetch_oldest_pending_assignment_for_curator, fetch_assignment_by_id
from learn_bot.db.utils.urls import is_valid_github_url, is_url_accessible, is_github_pull_request_url
from learn_bot.markups import compose_curator_menu_markup, compose_student_menu_markup, \
    compose_post_submit_assignment_markup, compose_curator_assignments_list_markup, \
    compose_curator_assignment_pull_request_check_markup
from learn_bot.screenplay.db.changers import get_or_create_user_from
from learn_bot.screenplay.db.fetchers import fetch_user_by_chat_id
from learn_bot.screenplay.services.play_act import play_active_act_for
from learn_bot.services.assignment import handle_new_assignment, handle_assignment_checked

logger = logging.getLogger(__name__)


def message_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        user = fetch_user_by_chat_id(message.chat.id, session)
    play_active_act_for(user, message, bot, config)


def start_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        user = get_or_create_user_from(
            message,
            session,
            active_screenplay_id='student.submit_assignment',
            active_act_id='intro',
        )
        play_active_act_for(user, message, bot, config)


##########################################################


def old_start_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    bot.reply_to(message, "start")
    return
    with bot.get_session() as session:
        curator = fetch_curator_by_telegram_nickname(message.from_user.username, session)
        student = fetch_student_by_telegram_nickname(message.from_user.username, session)

        if curator is not None:
            active_groups = [g for g in curator.groups if g.enrollment.is_active]
            active_groups_num = len(active_groups)
            groups_word = "группа" if active_groups_num == 1 else "группы"
            if curator.telegram_chat_id is None:
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
        elif student is not None:
            if student.telegram_chat_id is None:
                student.telegram_chat_id = message.chat.id
                update(student, session)
            active_group = student.group if student.group.enrollment.is_active else None
            if not active_group:
                bot.reply_to(
                    message,
                    (
                        f"Привет, {student.first_name}. Ты был нашим студентом, "
                        f"но сейчас у тебя нет активных групп. Всё равно будем знакомы!"
                    ),
                )
                return
            curator = active_group.curator
            bot.register_next_step_handler(
                message,
                functools.partial(submit_assignment_handle, bot=bot, config=config),
            )
            bot.reply_to(
                message,
                (
                    f"Привет, {student.first_name}. Твой куратор {curator.first_name} {curator.last_name}. "
                    f"А через меня можно сдавать задания на проверку."
                ),
                reply_markup=compose_student_menu_markup(),
            )
