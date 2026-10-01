"""Lesta Game Center: аналог VK Play, своего CLI нет."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from core.detector import find_in_registry
from platforms.base import DetectResult, GameState, Platform


WOT_PATHS = [
    r"C:\Games\Lesta\World_of_Tanks",
    r"C:\Program Files (x86)\Lesta\World_of_Tanks",
    r"%LOCALAPPDATA%\Lesta\World_of_Tanks",
]


class LestaPlatform(Platform):
    name = "lesta"

    def detect(self, game_id: str) -> DetectResult:
        for p in WOT_PATHS:
            path = Path(os.path.expandvars(p))
            if path.exists():
                return DetectResult(GameState.INSTALLED, install_path=str(path))
        loc = find_in_registry("Мир танков") or find_in_registry("World of Tanks")
        if loc:
            return DetectResult(GameState.INSTALLED, install_path=str(loc))
        return DetectResult(GameState.NOT_INSTALLED)

    def _launch(self, reason: str) -> bool:
        if not self.launcher_path:
            return False
        p = Path(os.path.expandvars(self.launcher_path))
        if not p.exists():
            self.log.error("Lesta LGC не найден: %s", p)
            return False
        try:
            subprocess.Popen([str(p)], close_fds=True)
            self.log.info("Lesta: запущен (%s)", reason)
            return True
        except OSError as e:
            self.log.error("Lesta start fail: %s", e)
            return False

    def install(self, game_id: str) -> bool:
        return self._launch(f"install {game_id}")

    def update(self, game_id: str) -> bool:
        return self._launch(f"update {game_id}")