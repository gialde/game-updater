"""Точка входа. Запускается из .exe. Читает config.yaml, ставит автозапуск, обходит игры."""
from __future__ import annotations

import sys
import time

from core.config import BASE_DIR, load_config
from core.orchestrator import Orchestrator
from utils import autostart
from utils.logger import setup_logger


def main() -> int:
    logger = setup_logger(BASE_DIR)

    try:
        cfg = load_config()
    except FileNotFoundError as e:
        logger.error(str(e))
        _pause_if_interactive()
        return 2

    if cfg.autostart_enabled:
        # Ставим/обновляем задачу только при запуске из собранного .exe.
        if getattr(sys, "frozen", False):
            autostart.install(cfg.task_name, logger)

    orchestrator = Orchestrator(cfg, logger)
    try:
        orchestrator.run()
    except Exception as e:  # noqa: BLE001
        logger.exception("Критическая ошибка: %s", e)
        return 1

    _pause_if_interactive()
    return 0


def _pause_if_interactive() -> None:
    """Чтобы окно не закрывалось при запуске двойным щелчком из исходников."""
    if not getattr(sys, "frozen", False) and sys.stdin and sys.stdin.isatty():
        try:
            input("\nНажмите Enter для выхода...")
        except EOFError:
            pass


if __name__ == "__main__":
    sys.exit(main())