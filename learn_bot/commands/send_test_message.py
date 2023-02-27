from learn_bot.bot import Bot
from learn_bot.config import BotConfig
from learn_bot.db.fetchers import fetch_curator_by_telegram_nickname


def run(bot: Bot, config: BotConfig) -> None:
    with bot.get_session() as session:
        curator = fetch_curator_by_telegram_nickname("melevir", session)
        bot.send_message(curator.telegram_chat_id, "Test message from bot")
