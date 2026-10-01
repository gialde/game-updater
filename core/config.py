"""Загрузка config.yaml и вычисление базовой директории."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


def base_dir() -> Path:
    """Папка рядом с .exe (при сборке) или с проектом (при запуске из исходников)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = base_dir()
CONFIG_PATH = BASE_DIR / "config.yaml"


@dataclass
class GameCfg:
    platform: str
    id: str
    name: str


@dataclass
class Config:
    autostart_enabled: bool = True
    task_name: str = "GameUpdater"
    launchers: dict[str, str] = field(default_factory=dict)
    games: list[GameCfg] = field(default_factory=list)
    delay_between_games_sec: int = 30


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Не найден {CONFIG_PATH}. Скопируйте config.example.yaml в config.yaml."
        )
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    cfg = Config()
    auto = raw.get("autostart") or {}
    cfg.autostart_enabled = bool(auto.get("enabled", True))
    cfg.task_name = str(auto.get("task_name", "GameUpdater"))
    cfg.launchers = {k: str(v) for k, v in (raw.get("launchers") or {}).items()}
    cfg.games = [
        GameCfg(platform=g["platform"], id=str(g["id"]), name=g["name"])
        for g in (raw.get("games") or [])
    ]
    cfg.delay_between_games_sec = int(raw.get("delay_between_games_sec", 30))
    return cfg