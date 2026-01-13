# Загрузчик справочников НСИ Минздрава России (прототип)

Сервис предназначен для периодической загрузки актуальных версий нормативно-справочных классификаторов из реестра НСИ Минздрава РФ через официальное REST API и их хранения в PostgreSQL в формате JSONB.

Полученная информация может использоваться в медицинских информационных системах, аналитических задачах или для обеспечения соответствия нормативным требованиям.

## Структура проекта

```
rnsi-integration-prototype/
├── app/
│   ├── __init__.py        # Инициализация пакета
│   ├── main.py            # FastAPI-приложение
│   ├── config.py          # Настройки и переменные окружения
│   ├── database.py        # Работа с PostgreSQL
│   └── nsi_client.py      # Клиент REST API НСИ
├── .env                       # Переменные окружения
├── .env.example               # Пример файла переменных окружения
├── docker-compose.yml         # Конфигурация Docker Compose
├── requirements.txt           # Python-зависимости
├── .gitignore                 # Исключаемые файлы
└── README.md                  # Документация проекта
```

## Требования

- Docker и docker-compose
- Python 3.11 или выше
- pip

## Быстрый старт

### 1. Подготовка окружения

Склонируйте репозиторий и создайте файл с конфигурацией:

```bash
cp .env.example .env
```

Откройте `.env` и укажите ваш ключ доступа `USER_KEY`, полученный в личном кабинете на сайте https://nsi.rosminzdrav.ru.

### 2. Запуск базы данных

```bash
docker compose up -d
```

Проверьте состояние контейнера:

```bash
docker compose ps
```

### 3. Создание таблицы (выполняется один раз)

```bash
docker exec -it nsi-postgres psql -U postgres -d dictionaries -c "
CREATE TABLE IF NOT EXISTS dictionary_records (
    id         SERIAL PRIMARY KEY,
    identifier TEXT NOT NULL,
    record     JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_identifier ON dictionary_records (identifier);
CREATE INDEX IF NOT EXISTS idx_record_gin ON dictionary_records USING GIN (record);
"
```

### 4. Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Запуск сервиса

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Интерактивная документация доступна по адресам:  
- Swagger UI: http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc

## Эндпоинты API

| Метод | Путь                          | Описание                                              |
|-------|-------------------------------|-------------------------------------------------------|
| GET   | `/dictionary`                 | Получить справочник по идентификатору без сохранения  |
| POST  | `/dictionary/save`            | Загрузить и сохранить один справочник в базу данных   |
| GET   | `/dictionary/download_all`    | Получить все настроенные справочники без сохранения   |
| POST  | `/dictionary/save_all`        | Загрузить и сохранить все настроенные справочники     |
| POST  | `/dictionary/sync_all`        | Полная синхронизация справочников (удобно для cron)   |

### Примеры запросов

```bash
# Получить один справочник
curl -X GET "http://127.0.0.1:8000/dictionary?identifier=1.2.643.5.1.13.13.11.1040"

# Сохранить один справочник
curl -X POST "http://127.0.0.1:8000/dictionary/save?identifier=1.2.643.5.1.13.13.11.1040"

# Сохранить все справочники
curl -X POST "http://127.0.0.1:8000/dictionary/save_all"

# Получить все справочники без сохранения
curl -X GET "http://127.0.0.1:8000/dictionary/download_all"

# Запуск синхронизации (для планировщика)
curl -X POST "http://127.0.0.1:8000/dictionary/sync_all"
```

## Обрабатываемые справочники

В конфигурации (`app/config.py`) по умолчанию заданы следующие классификаторы:

| Идентификатор                                   | Наименование                                      |
|-------------------------------------------------|---------------------------------------------------|
| 1.2.643.5.1.13.13.11.1040                       | Пол пациента                                      |
| 1.2.643.5.1.13.13.11.1486                       | Морфология новообразований                        |
| 1.2.643.5.1.13.13.99.2.647                      | Схемы лекарственной терапии                       |
| 1.2.643.5.1.13.13.99.2.1047                     | Молекулярно-генетические маркеры опухолей          |

Список можно дополнить или изменить в файле `app/config.py`.

## Проверка содержимого базы

```bash
docker exec -it nsi-postgres psql -U postgres -d dictionaries -c \
"SELECT identifier, COUNT(*) AS records_count 
 FROM dictionary_records 
 GROUP BY identifier 
 ORDER BY identifier;"
```

## Очистка данных (при необходимости начать сначала)

```bash
docker exec -it nsi-postgres psql -U postgres -d dictionaries -c \
"TRUNCATE TABLE dictionary_records RESTART IDENTITY;"
```