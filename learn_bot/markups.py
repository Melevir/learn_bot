from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def compose_curator_menu_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=1)
    markup.add(KeyboardButton('Посмотреть список работ'))
    return markup
