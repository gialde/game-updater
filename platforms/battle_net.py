"""Battle.net: своего CLI нет. Запускаем лаунчер — он сам проверит и обновит."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from core.detector import find_in_registry
from platforms.base import DetectResult, GameState, Platform


PRODUCT_NAMES = {
    "WTCG": "Hearthstone",
    "WoW": "World of Warcraft",
    "Pro": "Overwatch 2",
    "D3": "Diablo III",
}


class BattleNetPlatform(Platform):
    name = "battle_net"

    def detect(self, game_id: str) -> DetectResult:
        name = PRODUCT_NAMES.get(game_id, game_id)
        loc = find_in_registry(name)
        if loc:
            return DetectResult(GameState.INSTALLED, install_path=str(loc))
        if game_id == "WTCG":
            default = Path(r"C:\Program Files (x86)\Hearthstone")
            if default.exists():
                return DetectResult(GameState.INSTALLED, install_path=str(default))
        return DetectResult(GameState.NOT_INSTALLED)

    def _launch(self, reason: str) -> bool:
        if not self.launcher_path:
            self.log.error("Battle.net: путь к лаунчеру не задан")
            return False
        p = Path(os.path.expandvars(self.launcher_path))
        if not p.exists():
            self.log.error("Battle.net не найден: %s", p)
            return False
        try:
            subprocess.Popen([str(p)], close_fds=True)
            self.log.info("Battle.net: запущен (%s)", reason)
            return True
        except OSError as e:
            self.log.error("Battle.net start fail: %s", e)
            return False

    def install(self, game_id: str) -> bool:
        return self._launch(f"install {game_id}")

    def update(self, game_id: str) -> bool:
        return self._launch(f"update {game_id}")