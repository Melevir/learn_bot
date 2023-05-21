from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def compose_curator_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton("Посмотреть список работ"))
    return markup


def compose_student_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton("Сдать работу на проверку"))
    return markup


def compose_post_submit_assignment_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("Да, сдам ещё одну"))
    markup.add(KeyboardButton("Нет, пока хватит"))
    return markup


def compose_curator_assignments_list_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("Начать проверку"))
    markup.add(KeyboardButton("Позже"))
    return markup


def compose_curator_assignment_pull_request_check_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton("Готово"))
    return markup
