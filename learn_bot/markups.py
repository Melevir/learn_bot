from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def compose_curator_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton('Посмотреть список работ'))
    return markup


def compose_student_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton('Сдать работу на проверку'))
    return markup


def compose_post_submit_assignment_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton('Да, сдам ещё одну'))
    markup.add(KeyboardButton('Нет, пока хватит'))
    return markup
