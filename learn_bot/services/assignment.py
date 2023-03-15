from learn_bot.bot import Bot
from learn_bot.db import Assignment


def handle_new_assignment(assignment: Assignment, bot: Bot) -> None:
    curator = assignment.student.group.curator
    bot.send_message(curator.telegram_chat_id, f"{assignment.student.full_name} сдал работу на проверку")


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
    bot.send_message(assignment.student.telegram_chat_id, message)
