import functools
import logging

from telebot.types import Message

from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db import Assignment
from learn_bot.db.changers import update, create
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.fetchers import fetch_curator_by_telegram_nickname, fetch_student_by_telegram_nickname
from learn_bot.db.utils.urls import is_valid_github_url, is_url_accessible
from learn_bot.markups import compose_curator_menu_markup, compose_student_menu_markup, \
    compose_post_submit_assignment_markup
from learn_bot.services.assignment import handle_new_assignment

logger = logging.getLogger(__name__)


def start_handler(message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        curator = fetch_curator_by_telegram_nickname(message.from_user.username, session)
        student = fetch_student_by_telegram_nickname(message.from_user.username, session)

        if curator is not None:
            active_groups = [g for g in curator.groups if g.enrollment.is_active]
            active_groups_num = len(active_groups)
            groups_word = "группа" if active_groups_num == 1 else "группы"
            if curator.telegram_chat_id:
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



def list_pending_assignments_handle(message: Message, bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        curator = fetch_curator_by_telegram_nickname(message.from_user.username, session)
        if curator is None:
            return

        assignments = []
        reply_text = f"У тебя {len(assignments) or 'нет'} заданий на проверку"
        bot.reply_to(message, reply_text)


def submit_assignment_handle(message: Message, bot: Bot, config: BotConfig) -> None:
    bot.register_next_step_handler(
        message,
        functools.partial(create_assignment_handle, bot=bot, config=config),
    )
    bot.reply_to(
        message,
        "Скажи ссылку на Гитхаб с работой для проверки. Если у тебя несколько работ, сдавай их по одной",
    )


def create_assignment_handle(message: Message, bot: Bot, config: BotConfig) -> None:
    assignment_url = message.text
    if not is_valid_github_url(assignment_url):
        bot.register_next_step_handler(
            message,
            functools.partial(create_assignment_handle, bot=bot, config=config),
        )
        bot.reply_to(
            message,
            (
                "Это не похоже на ссылку на Гитхаб. Скажи ссылку на Гитхаб с работой для проверки. "
                "Если у тебя несколько работ, сдавай их по одной"
            ),
        )
        return
    elif not is_url_accessible(assignment_url):
        bot.register_next_step_handler(
            message,
            functools.partial(create_assignment_handle, bot=bot, config=config),
        )
        bot.reply_to(
            message,
            (
                "Я не вижу по этой ссылке работы. Пожалуйта, убедись, что ссылка правильная и "
                "сделай репозиторий на Гитхабе публичным"
            ),
        )
        return
    with bot.get_session() as session:
        student = fetch_student_by_telegram_nickname(message.from_user.username, session)
        assignment = Assignment(url=assignment_url, student_id=student.id, status=AssignmentStatus.READY_FOR_REVIEW)
        create(assignment, session)
        handle_new_assignment(assignment, bot)
        bot.register_next_step_handler(
            message,
            functools.partial(one_more_assignment_handle, bot=bot, config=config),
        )
        bot.reply_to(
            message,
            (
                f"Записал! Дам знать, как {student.group.curator.full_name} проверит твою работу. "
                f"Хочешь сдать ещё одну?"
            ),
            reply_markup=compose_post_submit_assignment_markup(),
        )


def one_more_assignment_handle(message: Message, bot: Bot, config: BotConfig) -> None:
    if message.text == 'Да, сдам ещё одну':
        return submit_assignment_handle(message, bot, config)
    else:
        bot.reply_to(message, "До скорого тогда")
