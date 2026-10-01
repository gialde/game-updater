"""Оркестратор: проходит по играм, детектит, делегирует установку/обновление лаунчеру."""
from __future__ import annotations

import time

from core.config import Config, GameCfg
from platforms.base import DetectResult, GameState
from platforms.steam import SteamPlatform
from platforms.epic import EpicPlatform
from platforms.battle_net import BattleNetPlatform
from platforms.vk_play import VKPlayPlatform
from platforms.lesta import LestaPlatform
from platforms.riot import RiotPlatform


PLATFORM_CLASSES = {
    "steam": SteamPlatform,
    "epic": EpicPlatform,
    "battle_net": BattleNetPlatform,
    "vk_play": VKPlayPlatform,
    "lesta": LestaPlatform,
    "riot": RiotPlatform,
}


class Orchestrator:
    def __init__(self, cfg: Config, logger):
        self.cfg = cfg
        self.log = logger

    def _platform(self, name: str):
        cls = PLATFORM_CLASSES.get(name)
        if not cls:
            return None
        return cls(self.cfg.launchers.get(name), self.log)

    def run(self) -> None:
        self.log.info("=== Проверка %d игр ===", len(self.cfg.games))
        for game in self.cfg.games:
            try:
                self._process(game)
            except Exception as e:  # noqa: BLE001 — оркестратор не должен падать
                self.log.exception("Игра %s: необработанная ошибка: %s", game.name, e)
            time.sleep(self.cfg.delay_between_games_sec)
        self.log.info("=== Готово ===")

    def _process(self, game: GameCfg) -> None:
        self.log.info("→ %s (%s)", game.name, game.platform)
        platform = self._platform(game.platform)
        if not platform:
            self.log.warning("Платформа '%s' не поддерживается", game.platform)
            return

        res: DetectResult = platform.detect(game.id)

        if res.state == GameState.NOT_INSTALLED:
            self.log.info("  не установлено → ставлю в очередь загрузки")
            platform.install(game.id)
            return

        if res.state == GameState.UPDATING:
            self.log.info("  уже обновляется (%s) — пропускаю", res.note)
            return

        if res.state == GameState.INSTALLED:
            self.log.info("  установлено (%s) → проверяю обновление", res.note)
            platform.update(game.id)
            return

        self.log.warning("  состояние неизвестно: %s", res.note)