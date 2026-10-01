"""VK Play: CLI не документирован. Детект по файлам, обновление — запуск GameCenter."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from platforms.base import DetectResult, GameState, Platform


WARFACE_PATHS = [
    r"C:\VK Play\Warface",
    r"C:\Games\VK Play\Warface",
    r"%LOCALAPPDATA%\VKPlay\Games\Warface",
    r"%PROGRAMFILES%\VK Play\Warface",
]


class VKPlayPlatform(Platform):
    name = "vk_play"

    def detect(self, game_id: str) -> DetectResult:
        for p in WARFACE_PATHS:
            path = Path(os.path.expandvars(p))
            if path.exists():
                return DetectResult(GameState.INSTALLED, install_path=str(path))
        return DetectResult(GameState.NOT_INSTALLED)

    def _launch(self, reason: str) -> bool:
        if not self.launcher_path:
            return False
        p = Path(os.path.expandvars(self.launcher_path))
        if not p.exists():
            self.log.error("VK Play GameCenter не найден: %s", p)
            return False
        try:
            subprocess.Popen([str(p)], close_fds=True)
            self.log.info("VK Play: запущен (%s)", reason)
            return True
        except OSError as e:
            self.log.error("VK Play start fail: %s", e)
            return False

    def install(self, game_id: str) -> bool:
        return self._launch(f"install {game_id}")

    def update(self, game_id: str) -> bool:
        return self._launch(f"update {game_id}")