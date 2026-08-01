# MariaDB → PostgreSQL Converter

Утилита для автоматической миграции SQL-дампов MariaDB/MySQL в PostgreSQL.

Проект предназначен для переноса нескольких SQL-файлов в одну базу PostgreSQL с использованием MariaDB в качестве промежуточного этапа и `pgloader` для конвертации.


# Архитектура

```

dbconverter/
  │
  ├── code/
  │    ├── __init__.py
  │    ├── config.py
  │    ├── convert.py
  │    └── logger.py
  │
  ├── dumps/
  │    └──  ваши_файлы.sql
  │
  ├── logs/
  │    ├── info.log
  │    └── error.log
  │
  ├── main.py
  ├── requirements.py
  └── README.md --------> Документация конвертера из MariaDB в PostgreeSQL

```

# Требования

Python 3.12+

MariaDB

PostgreSQL

pgloader

---

# Установка

```bash
git clone <repository>

cd db_converter

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```


# Использование

Положите все SQL-дампы в папку

```
dumps/
```

После этого выполнить

```bash
cd db_converter

python -m venv .venv

source .venv/bin/activate

python main
```

Конвертер автоматически выполнит весь процесс.

---

# Этапы работы

1. Поиск SQL-файлов
2. Объединение дампов
3. Создание временной MariaDB
4. Импорт полного SQL
5. Создание PostgreSQL
6. Запуск pgloader
7. Проверка результата
8. Очистка временных данных

---

# Логи

Во время работы создаются

```
logs/info.log

logs/error.log
```

---

# Временные файлы

Все временные SQL создаются в

```
temp/
```

После успешной миграции автоматически удаляются.

---

# Результат

После успешного завершения проекта в PostgreSQL появляется готовая база данных.

Временная база MariaDB удаляется автоматически.
