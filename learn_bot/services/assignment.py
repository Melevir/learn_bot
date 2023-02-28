from learn_bot.bot import Bot
from learn_bot.db import Assignment


def handle_new_assignment(assignment: Assignment, bot: Bot) -> None:
    curator = assignment.student.group.curator
    bot.send_message(curator.telegram_chat_id, f"{assignment.student.full_name} сдал работу на проверку")
