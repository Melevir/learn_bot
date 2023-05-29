import logging

from learn_bot.bot import Bot
from learn_bot.db import Assignment
from learn_bot.markups import compose_curator_check_single_assignment_markup
from learn_bot.screenplay.db.changers import get_or_create_screenplay_request
from learn_bot.screenplay.db.fetchers import fetch_user_by_chat_id, fetch_user_by_telegram_nickname

logger = logging.getLogger(__name__)


def handle_new_assignment(assignment: Assignment, bot: Bot) -> None:
    with bot.get_session() as session:
        curator = assignment.student.group.curator
        curator_user = fetch_user_by_telegram_nickname(curator.telegram_nickname, session)
    if curator_user and curator_user.telegram_chat_id:
        play_request = get_or_create_screenplay_request(
            screenplay_id="curator.check_assignment",
            act_id="check",
            context={"assignment_id": str(assignment.id), "check_single_assignment": "true"},
            session=session,
        )
        markup = compose_curator_check_single_assignment_markup(play_request.id)
        bot.send_message(
            curator_user.telegram_chat_id,
            f"{assignment.student.full_name} сдал работу на проверку",
            reply_markup=markup,
        )
    else:
        logger.error(f"Not found curator telegram_chat_id ({curator.telegram_nickname})")


def handle_assignment_checked(assignment: Assignment, bot: Bot) -> None:
    curator = assignment.student.group.curator
    if assignment.curator_feedback:
        message = (
            f"{curator.first_name} проверил твоё задание ({assignment.url}). "
            f"Вот его комментарии:\n{assignment.curator_feedback}"
        )
    else:
        message = (
            f"{curator.first_name} проверил твоё задание ({assignment.url}). "
            f"Комментарии в пул-реквеста на Гитхабе"
        )
    with bot.get_session() as session:
        student_user = (
            fetch_user_by_telegram_nickname(assignment.student.telegram_nickname, session)
            or fetch_user_by_chat_id(assignment.student.telegram_chat_id, session)
        )
    if student_user and student_user.telegram_chat_id:
        bot.send_message(student_user.telegram_chat_id, message)
    else:
        logger.error(f"Not found student telegram_chat_id ({assignment.student.telegram_nickname})")
