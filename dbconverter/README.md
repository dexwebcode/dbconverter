# MariaDB → PostgreSQL Converter

Утилита для автоматической миграции SQL-дампов MariaDB/MySQL в PostgreSQL.

Проект предназначен для переноса нескольких SQL-файлов в одну базу PostgreSQL с использованием MariaDB в качестве промежуточного этапа и `pgloader` для конвертации.

---

# Возможности

- автоматический поиск SQL-файлов;
- объединение нескольких дампов в один;
- создание временной базы MariaDB;
- импорт полного дампа;
- автоматическое создание PostgreSQL;
- перенос данных через pgloader;
- проверка результата;
- очистка временных файлов.

---

# Архитектура

```
SQL Dumps
     │
     ▼
Merge SQL Files
     │
     ▼
full_dump.sql
     │
     ▼
MariaDB (migration_temp)
     │
     ▼
pgloader
     │
     ▼
PostgreSQL (kingpromotion)
     │
     ▼
Validation
     │
     ▼
Cleanup
```

---

# Структура проекта

```
db_converter/

├── config/
│   └── config.yaml
│
├── converter/
│   ├── maria.py
│   ├── postgres.py
│   ├── merger.py
│   ├── validator.py
│   ├── pgloader.py
│   ├── utils.py
│   └── logger.py
│
├── dumps/
│
├── logs/
│
├── temp/
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

---

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

---

# Настройка

Заполнить файл

```
config/config.yaml
```

Пример:

```yaml
mariadb:

  host: localhost

  port: 3306

  user: converter

  password: converter123

postgres:

  host: localhost

  port: 5432

  user: king

  password: king123

  database: kingpromotion
```

---

# Использование

Положить все SQL-дампы в папку

```
dumps/
```

После этого выполнить

```bash
python main.py
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