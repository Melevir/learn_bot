from typing import Type

from learn_bot.db.base import Base


def fetch_all_models() -> list[Type[Base]]:
    return [m.class_ for m in Base.registry.mappers]
