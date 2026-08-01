
import logging

from .config import config


class LoggerManager:
    """Класс для управления логами."""

    def __init__(self):
        """Инициализация класса."""
        self.log_dir = config.paths.logs
        self.logger = None

    def setup_logging(self):
        """Настройка окружения логгера, создание папок и файлов логов."""
        self.log_dir.mkdir(parents=True, exist_ok=True)

        debug_path = self.log_dir / config.logger.filename
        info_path = self.log_dir / "info.log"
        error_path = self.log_dir / "error.log"

        if self.logger is None:
            self.logger = logging.getLogger("db_converter")
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False

            if self.logger.handlers:
                return self.logger

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            debug_handler = logging.FileHandler(debug_path, encoding="utf-8")
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            self.logger.addHandler(debug_handler)

            info_handler = logging.FileHandler(info_path, encoding="utf-8")
            info_handler.setLevel(logging.INFO)
            info_handler.setFormatter(formatter)
            self.logger.addHandler(info_handler)

            error_handler = logging.FileHandler(error_path, encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            self.logger.debug("Логирование настроено")
            self.logger.debug("Файл подробного лога: %s", debug_path)
            self.logger.debug("Файл информационного лога: %s", info_path)
            self.logger.debug("Файл ошибок: %s", error_path)

        return self.logger


def get_logger():
    """Вспомогательная функция для получения логгера."""
    manager = LoggerManager()
    return manager.setup_logging()


logger = get_logger()
