"""Автозапуск .exe при логоне через Task Scheduler.

Использует schtasks — встроенную утилиту Windows, доступна без зависимостей.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _exe_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    # При запуске из исходников: python.exe + main.py — не поддерживаем автозапуск.
    return Path("")


def install(task_name: str = "GameUpdater", logger=None) -> bool:
    """Создать или перезаписать задачу автозапуска. Требует прав администратора."""
    exe = _exe_path()
    if not exe or not exe.exists():
        if logger:
            logger.warning("Автозапуск ставится только из собранного .exe")
        return False

    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{exe}"',
        "/sc", "onlogon",
        "/rl", "highest",
        "/f",
    ]
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, encoding="cp866", check=False
        )
    except OSError as e:
        if logger:
            logger.error("schtasks не запустился: %s", e)
        return False

    if res.returncode == 0:
        if logger:
            logger.info("Задача автозапуска '%s' установлена", task_name)
        return True

    if logger:
        logger.error("schtasks вернул код %s: %s", res.returncode, res.stderr.strip())
    return False


def uninstall(task_name: str = "GameUpdater", logger=None) -> bool:
    try:
        res = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            capture_output=True, text=True, encoding="cp866", check=False,
        )
        return res.returncode == 0
    except OSError:
        return False