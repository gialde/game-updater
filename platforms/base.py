"""Базовый контракт платформы."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class GameState(str, Enum):
    INSTALLED = "installed"          # установлено и актуально
    NOT_INSTALLED = "not_installed"
    UPDATING = "updating"            # лаунчер уже качает/ставит
    UNKNOWN = "unknown"


@dataclass
class DetectResult:
    state: GameState
    install_path: str | None = None
    version: str | None = None
    note: str = ""


class Platform(ABC):
    name: str = "base"

    def __init__(self, launcher_path: str | None, logger):
        self.launcher_path = launcher_path
        self.log = logger

    @abstractmethod
    def detect(self, game_id: str) -> DetectResult: ...

    @abstractmethod
    def install(self, game_id: str) -> bool: ...

    @abstractmethod
    def update(self, game_id: str) -> bool: ...