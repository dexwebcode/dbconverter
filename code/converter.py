import shutil
import subprocess
from pathlib import Path

from .config import config, log_config_summary
from .logger import logger


class Converter:

    def __init__(self):
        self.dumps = config.paths.dumps
        self.temp = config.paths.temp

        self.full_dump = self.temp / "full_dump.sql"
        log_config_summary(config)
        logger.debug("Converter инициализирован")

    # ----------------------------------------------------

    def run(self):
        logger.info("========== КОНВЕРТАЦИЯ НАЧАТА ==========")

        try:
            self.merge_sql_files()

            self.create_mariadb()

            self.import_dump()

            self.create_postgresql()

            self.run_pgloader()

            self.validate()

            self.drop_mariadb()

            self.remove_temp()
        except Exception:
            logger.exception("Конвертация завершилась с ошибкой")
            raise

        logger.info("========== ГОТОВО ==========")

    # ----------------------------------------------------

    def merge_sql_files(self):
        """
        Объединяет все SQL-файлы из dumps/ в один temp/full_dump.sql.
        """
        logger.info("=" * 60)
        logger.info("Сборка общего SQL-дампа")
        logger.info("=" * 60)
        logger.debug("Папка дампов: %s", self.dumps)
        logger.debug("Временная папка: %s", self.temp)
        logger.debug("Итоговый дамп: %s", self.full_dump)

        # Создаем temp/, если его нет
        self.temp.mkdir(parents=True, exist_ok=True)
        logger.debug("Временная папка готова")

        # Удаляем старый full_dump.sql
        if self.full_dump.exists():
            logger.debug("Удаляем старый файл: %s", self.full_dump)
            self.full_dump.unlink()

        # Получаем список всех SQL-файлов
        sql_files = sorted(self.dumps.glob("*.sql"))
        logger.debug("SQL-файлы для объединения: %s", [file.name for file in sql_files])

        if not sql_files:
            logger.error("В папке '%s' не найдено ни одного .sql файла", self.dumps)
            raise FileNotFoundError(
                f"В папке '{self.dumps}' не найдено ни одного .sql файла."
            )

        logger.info(f"Найдено файлов: {len(sql_files)}")

        # Создаем объединенный дамп
        with open(self.full_dump, "wb") as outfile:

            for file in sql_files:

                logger.info(f"Добавление: {file.name}")
                logger.debug("Размер файла %s: %s байт", file.name, file.stat().st_size)

                with open(file, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)

                # Добавляем пустую строку между файлами
                outfile.write(b"\n\n")

        logger.info(f"Общий дамп успешно создан:")
        logger.info(self.full_dump)
        logger.debug("Размер общего дампа: %s байт", self.full_dump.stat().st_size)

    # ----------------------------------------------------

    def _mask_secrets(self, command: str) -> str:
        """Маскирует пароли в командах перед записью в лог."""
        masked = command
        for secret in (config.mariadb.password, config.postgres.password):
            if secret:
                masked = masked.replace(secret, "***")
        return masked

    def _run_command(self, title: str, command: str) -> subprocess.CompletedProcess:
        """Запускает shell-команду и пишет результат в лог."""
        logger.info(title)
        logger.debug("Команда:\n%s", self._mask_secrets(command).strip())

        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                timeout=config.app.timeout,
            )
        except subprocess.CalledProcessError as exc:
            logger.error("%s завершилась с кодом %s", title, exc.returncode)
            if exc.stdout:
                logger.error("stdout:\n%s", exc.stdout.strip())
            if exc.stderr:
                logger.error("stderr:\n%s", exc.stderr.strip())
            raise
        except subprocess.TimeoutExpired:
            logger.error("%s превысила таймаут %s секунд", title, config.app.timeout)
            raise

        if result.stdout:
            logger.debug("stdout:\n%s", result.stdout.strip())
        if result.stderr:
            logger.debug("stderr:\n%s", result.stderr.strip())
        logger.info("%s выполнена успешно", title)
        return result

    def create_mariadb(self):
        command = f'''
MYSQL_PWD="{config.mariadb.password}" mariadb \
-h {config.mariadb.host} \
-u {config.mariadb.user} \
-e "
DROP DATABASE IF EXISTS migration_temp;

CREATE DATABASE migration_temp
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
"
'''

        self._run_command("Создание временной MariaDB", command)

    # ----------------------------------------------------

    def import_dump(self):
        if not self.full_dump.exists():
            logger.error("Файл дампа не найден перед импортом: %s", self.full_dump)
            raise FileNotFoundError(f"Файл дампа не найден: {self.full_dump}")

        command = f'''
MYSQL_PWD="{config.mariadb.password}" mariadb \
-h {config.mariadb.host} \
-u {config.mariadb.user} \
migration_temp < {self.full_dump}
'''

        self._run_command("Импорт full_dump.sql в MariaDB", command)

    # ----------------------------------------------------

    def create_postgresql(self):
        drop = f'''
PGPASSWORD="{config.postgres.password}" psql \
-h {config.postgres.host} \
-U {config.postgres.user} \
-d postgres \
-c "DROP DATABASE IF EXISTS kingpromotion;"
'''

        create = f'''
PGPASSWORD="{config.postgres.password}" psql \
-h {config.postgres.host} \
-U {config.postgres.user} \
-d postgres \
-c "CREATE DATABASE kingpromotion;"
'''

        self._run_command("Удаление старой PostgreSQL-базы kingpromotion", drop)
        self._run_command("Создание PostgreSQL-базы kingpromotion", create)

    # ----------------------------------------------------

    def run_pgloader(self):
        command = f'''
pgloader \
mysql://{config.mariadb.user}:{config.mariadb.password}@localhost/migration_temp \
postgresql://{config.postgres.user}:{config.postgres.password}@localhost/kingpromotion
'''

        self._run_command("Запуск pgloader", command)

    # ----------------------------------------------------

    def validate(self):

        logger.info("Проверка данных...")

        logger.info("Проверка будет реализована позже.")
        logger.debug(
            "Настройки проверки: validate_rows=%s validate_tables=%s",
            config.app.validate_rows,
            config.app.validate_tables,
        )

    # ----------------------------------------------------

    def drop_mariadb(self):
        command = f'''
MYSQL_PWD="{config.mariadb.password}" mariadb \
-h {config.mariadb.host} \
-u {config.mariadb.user} \
-e "DROP DATABASE migration_temp;"
'''

        self._run_command("Удаление временной MariaDB migration_temp", command)

    # ----------------------------------------------------

    def remove_temp(self):
        if self.temp.exists():
            logger.debug("Удаление временной папки: %s", self.temp)
            shutil.rmtree(self.temp)

            logger.info(f"Удалена папка: {self.temp}")
        else:
            logger.debug("Временная папка отсутствует, удаление не требуется: %s", self.temp)

