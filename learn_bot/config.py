import dataclasses
import os


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class BotConfig:
    telegram_token: str


def get_config() -> BotConfig:
    return BotConfig(
        telegram_token=os.environ.get("TELEGRAM_BOT_TOKEN"),
    )
