from __future__ import annotations

import dataclasses

from learn_bot.screenplay.custom_types import PlayHandler, ScreenPlay


@dataclasses.dataclass()
class ScreenplayDirector:
    _handlers: dict[str, dict[str, PlayHandler]] | None = None

    def register_play(self, play: ScreenPlay) -> None:
        if self._handlers is None:
            self._handlers = {}
        self._handlers[play.name] = dict(play.acts)

    def fetch_act_handler(
        self,
        screenplay_id: str,
        act_id: str,
    ) -> PlayHandler:
        return self._handlers[screenplay_id][act_id]
