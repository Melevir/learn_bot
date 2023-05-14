from __future__ import annotations

import dataclasses

from learn_bot.screenplay.custom_types import PlayHandler, ScreenPlay


@dataclasses.dataclass()
class ScreenplayDirector:
    _handlers: dict[str, ScreenPlay] | None = None

    def register_play(self, play: ScreenPlay) -> None:
        if self._handlers is None:
            self._handlers = {}
        self._handlers[play.name] = play

    def fetch_act_handler(
        self,
        screenplay_id: str,
        act_id: str,
    ) -> PlayHandler:
        return dict(self._handlers[screenplay_id].acts)[act_id]

    def fetch_plays_for_role(self, role: str) -> list[ScreenPlay]:
        return [h for h in self._handlers.values() if role in h.allowed_for_roles]
