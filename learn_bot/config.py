import dataclasses
import os


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class BotConfig:
    telegram_token: str
    db_dsn: str
    db_echo: bool


def get_config() -> BotConfig:
    return BotConfig(
        telegram_token=os.environ.get("TELEGRAM_BOT_TOKEN"),
        db_dsn=os.environ.get("DATABASE_DSN"),
        db_echo="DATABASE_ECHO" in os.environ,
    )
