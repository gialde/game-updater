"""Riot Client: запускаем RiotClientServices.exe с --launch-product."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from platforms.base import DetectResult, GameState, Platform


PRODUCTS = {
    "league_of_legends": ("league_of_legends", "live"),
    "valorant":          ("valorant",          "live"),
}


class RiotPlatform(Platform):
    name = "riot"

    def detect(self, game_id: str) -> DetectResult:
        product, _ = PRODUCTS.get(game_id, (game_id, "live"))
        candidates = [
            Path(rf"C:\Riot Games\{product}"),
            Path(rf"C:\Riot Games\{product.capitalize()}"),
            Path(rf"C:\Riot Games\{product.replace('_', ' ').title()}"),
        ]
        for c in candidates:
            if c.exists():
                return DetectResult(GameState.INSTALLED, install_path=str(c))
        return DetectResult(GameState.NOT_INSTALLED)

    def _launch(self, product: str, patchline: str, reason: str) -> bool:
        if not self.launcher_path:
            return False
        exe = Path(os.path.expandvars(self.launcher_path))
        if not exe.exists():
            self.log.error("Riot Client не найден: %s", exe)
            return False
        args = [
            str(exe),
            f"--launch-product={product}",
            f"--launch-patchline={patchline}",
        ]
        try:
            subprocess.Popen(args, close_fds=True)
            self.log.info("Riot: запущен %s (%s)", product, reason)
            return True
        except OSError as e:
            self.log.error("Riot start fail: %s", e)
            return False

    def install(self, game_id: str) -> bool:
        product, line = PRODUCTS.get(game_id, (game_id, "live"))
        return self._launch(product, line, "install")

    def update(self, game_id: str) -> bool:
        product, line = PRODUCTS.get(game_id, (game_id, "live"))
        return self._launch(product, line, "update")