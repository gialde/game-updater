"""Epic: официальный URI-протокол com.epicgames.launcher://apps/<name>?action=install|launch."""
from __future__ import annotations

import os
from pathlib import Path

from core.detector import find_in_registry
from platforms.base import DetectResult, GameState, Platform


MANIFESTS_DIR = Path(r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests")

# Отображаемое имя → внутреннее имя приложения Epic.
APP_NAMES = {
    "Fortnite": "Fortnite",
    "Fall Guys": "FallGuys",
    "FallGuys": "FallGuys",
}


class EpicPlatform(Platform):
    name = "epic"

    def detect(self, game_id: str) -> DetectResult:
        if MANIFESTS_DIR.exists():
            needle = game_id.lower()
            for mf in MANIFESTS_DIR.glob("*.item"):
                try:
                    text = mf.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if needle in text.lower():
                    return DetectResult(GameState.INSTALLED, note=mf.name)
        loc = find_in_registry(game_id)
        if loc:
            return DetectResult(GameState.INSTALLED, install_path=str(loc))
        return DetectResult(GameState.NOT_INSTALLED)

    def _uri(self, app: str, action: str) -> str:
        return f"com.epicgames.launcher://apps/{app}?action={action}"

    def _open(self, uri: str) -> bool:
        try:
            os.startfile(uri)  # noqa: S606
            return True
        except OSError as e:
            self.log.error("Epic URI fail: %s", e)
            return False

    def _app(self, game_id: str) -> str:
        return APP_NAMES.get(game_id, game_id)

    def install(self, game_id: str) -> bool:
        app = self._app(game_id)
        self.log.info("Epic: install %s", app)
        return self._open(self._uri(app, "install"))

    def update(self, game_id: str) -> bool:
        app = self._app(game_id)
        self.log.info("Epic: launch %s (обновление подхватит клиент)", app)
        return self._open(self._uri(app, "launch"))