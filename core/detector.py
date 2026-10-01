"""Универсальный детектор: установлена ли программа, через реестр Windows."""
from __future__ import annotations

import os
import winreg
from pathlib import Path

UNINSTALL_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]


def _iter_uninstall_subkeys():
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for sub in UNINSTALL_KEYS:
            try:
                with winreg.OpenKey(root, sub) as key:
                    n = winreg.QueryInfoKey(key)[0]
                    for i in range(n):
                        try:
                            name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, name) as subkey:
                                yield subkey
                        except OSError:
                            continue
            except FileNotFoundError:
                continue


def find_in_registry(display_name_substr: str) -> Path | None:
    """Ищет установленное ПО по подстроке в DisplayName. Возвращает InstallLocation или путь из DisplayIcon."""
    needle = display_name_substr.lower()
    for subkey in _iter_uninstall_subkeys():
        try:
            name, _ = winreg.QueryValueEx(subkey, "DisplayName")
        except OSError:
            continue
        if needle not in str(name).lower():
            continue
        for field in ("InstallLocation", "DisplayIcon"):
            try:
                val, _ = winreg.QueryValueEx(subkey, field)
                if val:
                    return Path(str(val).strip('"'))
            except OSError:
                continue
    return None


def exists_any(*paths: str) -> Path | None:
    """Первый существующий путь с подстановкой переменных окружения."""
    for p in paths:
        expanded = Path(os.path.expandvars(p))
        if expanded.exists():
            return expanded
    return None