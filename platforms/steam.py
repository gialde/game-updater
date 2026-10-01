"""Steam: детект через appmanifest, установка и обновление через URI steam://."""
from __future__ import annotations

import os
import re
import winreg
from pathlib import Path

from platforms.base import DetectResult, GameState, Platform


_VDF_PATH = re.compile(r'"path"\s+"([^"]+)"')
_ACF_KV = re.compile(r'"(\w+)"\s+"([^"]*)"')


def _steam_root_from_registry() -> Path | None:
    for hive, sub in (
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
    ):
        try:
            with winreg.OpenKey(hive, sub) as k:
                path, _ = winreg.QueryValueEx(k, "SteamPath")
                return Path(str(path))
        except OSError:
            continue
    return None


def _library_folders(root: Path) -> list[Path]:
    libs = [root]
    vdf = root / "steamapps" / "libraryfolders.vdf"
    if vdf.exists():
        try:
            text = vdf.read_text(encoding="utf-8", errors="ignore")
            for m in _VDF_PATH.finditer(text):
                p = Path(m.group(1).replace("\\\\", "\\"))
                if p.exists() and p not in libs:
                    libs.append(p)
        except OSError:
            pass
    return libs


def _appmanifest(root: Path, app_id: str) -> Path | None:
    for lib in _library_folders(root):
        p = lib / "steamapps" / f"appmanifest_{app_id}.acf"
        if p.exists():
            return p
    return None


def _parse_acf(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    return {k: v for k, v in _ACF_KV.findall(text)}


class SteamPlatform(Platform):
    name = "steam"

    def __init__(self, launcher_path: str | None, logger):
        super().__init__(launcher_path, logger)
        self._root: Path | None = None

    def _root_dir(self) -> Path | None:
        if self._root and self._root.exists():
            return self._root
        self._root = _steam_root_from_registry()
        if not self._root and self.launcher_path:
            p = Path(os.path.expandvars(self.launcher_path)).parent
            if p.exists():
                self._root = p
        return self._root

    def detect(self, game_id: str) -> DetectResult:
        root = self._root_dir()
        if not root:
            return DetectResult(GameState.UNKNOWN, note="Steam не найден")
        mf = _appmanifest(root, game_id)
        if not mf:
            return DetectResult(GameState.NOT_INSTALLED, note="appmanifest отсутствует")
        data = _parse_acf(mf)
        # StateFlags=4 означает «полностью установлено».
        flags = data.get("StateFlags", "")
        if flags == "4":
            return DetectResult(
                GameState.INSTALLED,
                install_path=data.get("installdir", ""),
                version=data.get("buildid", ""),
                note=f"buildid={data.get('buildid', '?')}",
            )
        return DetectResult(
            GameState.UPDATING,
            install_path=data.get("installdir", ""),
            version=data.get("buildid", ""),
            note=f"StateFlags={flags}",
        )

    def _open_uri(self, uri: str) -> bool:
        try:
            os.startfile(uri)  # noqa: S606 — Windows-специфично
            return True
        except OSError as e:
            self.log.error("Steam URI '%s' не открылся: %s", uri, e)
            return False

    def install(self, game_id: str) -> bool:
        self.log.info("Steam: install appid=%s", game_id)
        return self._open_uri(f"steam://install/{game_id}")

    def update(self, game_id: str) -> bool:
        # rungameid заставляет клиент проверить обновления и поставить их.
        self.log.info("Steam: update appid=%s", game_id)
        return self._open_uri(f"steam://rungameid/{game_id}")