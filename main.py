import sys

try:
    from .code.converter import Converter
    from .code.logger import logger
except ImportError:
    from code.converter import Converter
    from code.logger import logger


def main() -> int:
    """Точка входа приложения."""
    logger.info("Запуск dbconverter")

    try:
        converter = Converter()
        converter.run()
    except Exception:
        logger.exception("dbconverter завершился с ошибкой")
        return 1

    logger.info("dbconverter завершился успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
