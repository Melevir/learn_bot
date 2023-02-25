import logging

import coloredlogs
from telebot import logger as telebot_logger


def configure_logging() -> None:
    telebot_logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    coloredlogs.install(level=logging.DEBUG)
