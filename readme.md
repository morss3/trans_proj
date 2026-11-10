# MUT Transport Bot

Чат-бот для информирования пассажиров о задержках транспорта. Отвечает на вопросы на естественном языке, ищет инциденты в векторной базе и (в планах) — в реляционной БД для точных фактов.

## Стек

- **Python 3.12** — язык разработки
- **LangGraph** — оркестрация агента (граф состояний)
- **LangChain** — интеграции с LLM и Qdrant
- **Qdrant** — векторная БД для семантического поиска (RAG)
- **HuggingFace Embeddings** (`intfloat/multilingual-e5-small`) — локальные эмбеддинги (размерность 384)
- **OpenRouter (Qwen)** — LLM для формулировки ответов (с абстракцией под DeepSeek)
- **Docker** — контейнеризация Qdrant
- **SQLite** — реляционная БД для точных фактов (в разработке)

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/ТВОЙ_НИК/mut-transport-bot.git
cd mut-transport-bot
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Создать `.env`

```env
OPENROUTER_API_KEY=твой_ключ_с_openrouter
```

> **Важно:** `.env` не коммитится в git (см. `.gitignore`).

### 4. Запустить Qdrant в Docker

```bash
docker compose up -d
```

Проверка: `docker ps` — контейнер `qdrant` должен быть `Up`.

### 5. Загрузить тестовые данные в Qdrant

```bash
python seed_qdrant.py
```

### 6. Запустить агента

```bash
python agent.py
```

## Структура проекта

```
├── agent.py              # LangGraph-агент + инструмент поиска в Qdrant
├── seed_qdrant.py        # Загрузка тестовых данных в Qdrant
├── settings.py           # Настройки LLM (OpenRouter / Qwen)
├── contract.py           # Контракты между модулями (сигнатуры функций)
├── docker-compose.yaml   # Qdrant в Docker
├── .env                  # Секреты (не коммитится)
├── .gitignore
└── README.md
```

## Как это работает

1. Пользователь задаёт вопрос: «Почему трамвай 5 стоит на Ленина?»
2. Агент (LangGraph) решает вызвать инструмент `search_incidents`.
3. Вопрос превращается в вектор моделью `multilingual-e5-small`.
4. Qdrant находит семантически близкие тексты инцидентов.
5. LLM (Qwen через OpenRouter) формулирует ответ на основе найденного.

## Статус

- [x] RAG-поиск в Qdrant (Контракт 4)
- [ ] Function Calling к SQLite — точные факты (Контракт 3)
- [ ] Админ-панель диспетчера
- [ ] Боты Telegram и ВК
- [ ] Подписки на маршруты и уведомления

## Примечания

- На Windows с VPN добавлен `NO_PROXY=localhost,127.0.0.1`, чтобы Qdrant-клиент ходил напрямую, а OpenRouter — через VPN.
- Эмбеддинги локальные, не зависят от внешних API.
- LLM абстрагирована: замена OpenRouter на DeepSeek — смена `base_url` и модели в `settings.py`.

## Лицензия

Учебный проект. Кейс МУТ «Метроэлектротранс».