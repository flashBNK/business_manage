# business_manage

Учебный pet-проект: система управления компанией на микросервисной архитектуре: аутентификация, оргструктура и задачник. Три независимых сервиса на FastAPI, каждый со своей базой PostgreSQL, общаются между собой асинхронно через Kafka.

## Архитектура


### Сервисы

**auth_service** - пользователи, аккаунты, компании, участники, аутентификация.
Регистрация по коду на почту, инвайты сотрудников, JWT (RS256) + refresh-токены, роли owner/admin/member в рамках компании.

**org_service** - оргструктура компании.
Дерево подразделений в PostgreSQL `ltree`, должности, назначение сотрудников на должности, руководители подразделений.

**tasks_service** - задачник.
Задачи с автором, ответственным, наблюдателями и исполнителями; дедлайн, статус, оценка времени.

### Межсервисное взаимодействие

Через Kafka.

- **Transactional outbox** - событие пишется в таблицу outbox_event в одной транзакции с бизнес-данными, фоновый relay публикует его в Kafka и проставляет "published_at".
- **Inbox** - консьюмер записывает "(consumer_name, event_id)" в "inbox_event" в одной транзакции с применением изменений, что делает его идемпотентным.
- **Envelope** - конверт события: "event_id", "event_type", "aggregate_id", "correlation_id", "causation_id", "occurred_at", "schema_version" "producer" и "payload".
- **Партиционирование** по "aggregate_id" - события одной сущности обрабатываются строго по порядку.
- **Реплики** - org_service и tasks_service держат у себя минимальные копии данных о пользователях, компаниях, наполняемые auth_service.

JWT подписывается приватным ключом только auth_service, остальные сервисы умеют только проверять подпись.

### Сага регистрации

Регистрация компании - распределённая транзакция с компенсацией. auth_service - оркестратор, состояние хранится в таблице "registration_saga".

Если любой шаг падает, оркестратор рассылает компенсирующие команды ("registration.org.compensate"), откатывая созданные данные в остальных сервисах.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy 2.0 (async) 
- PostgreSQL 17 
- Alembic 
- Kafka (aiokafka)
- Pydantic 
- structlog 
- PyJWT 
- Argon2
- pytest
- Ruff
- poetry

## Запуск

Нужен Docker и Docker Compose.

```bash
git clone https://github.com/flashBNK/business_manage.git
cd business_manage
```

Скопируйте ".env.example" в ".env" корне проекта и подставьте свои данные

Сгенерировать пару ключей для JWT и разложить публичный ключ по всем сервисам:

```bash
mkdir -p auth_service/config/keys org_service/config/keys tasks_service/config/keys
openssl genrsa -out auth_service/config/keys/jwt-private.pem 2048
openssl rsa -in auth_service/config/keys/jwt-private.pem -pubout -out auth_service/config/keys/jwt-public.pem
cp auth_service/config/keys/jwt-public.pem org_service/config/keys/
cp auth_service/config/keys/jwt-public.pem tasks_service/config/keys/
```

Поднять всё:

```bash
docker compose up --build
```

Накатить миграции (каждому сервису — свои):

```bash
docker compose exec -w /app/auth_service auth_service alembic upgrade head
docker compose exec -w /app/org_service/src org_service alembic upgrade head
docker compose exec -w /app/tasks_service/src tasks_service alembic upgrade head
```

## Порты

| Сервис | API | Swagger | PostgreSQL |
| --- | --- | --- | --- |
| auth_service | 8000 | http://localhost:8000/docs | 5433 |
| org_service | 8001 | http://localhost:8001/docs | 5434 |
| tasks_service | 8002 | http://localhost:8002/docs | 5435 |
| Kafka | — | — | 9092 (только `127.0.0.1`) |

## API

Все защищённые ручки требуют заголовок Authorization: Bearer {access_token}.

**auth_service** — `/api/v1`

```
POST   /check_account                        проверка почты, отправка кода
POST   /sign-up                              подтверждение кода
POST   /sign-up-complete                     завершение регистрации, выдача токенов
POST   /login                                вход
POST   /refresh                              обновление пары токенов
POST   /logout                               отзыв refresh-токена
GET    /me                                   текущий пользователь
PATCH  /me                                   редактирование профиля
GET    /me/accounts                          список привязанных почт
POST   /account/{account_id}                 запрос смены почты
POST   /account/{account_id}/update-complete  подтверждение смены почты
POST   /companies/{company_id}/employees     создание сотрудника (админ)
POST   /employees/invite-complete            завершение регистрации по инвайту
```

**org_service** — `/api/v1/companies/{company_id}`

```
POST   /structure/{parent_id}/children          создать подразделение
GET    /structure                               дерево компании
GET    /structure/{id}                          подразделение
GET    /structure/{id}/children | /descendants | /ancestors
PATCH  /structure/{id}                          переименовать
PATCH  /structure/{id}/move                     переместить поддерево
DELETE /structure/{id}
PUT    /structure/{id}/manager                  назначить руководителя
GET    /structure/{id}/manager
DELETE /structure/{id}/manager
POST   /positions                               создать должность
GET    /positions | /positions/{id}
PATCH  /positions/{id}
DELETE /positions/{id}
POST   /structure/{id}/positions/{position_id}  привязать должность к подразделению
GET    /structure/{id}/positions
DELETE /structure/{id}/positions/{position_id}
POST   /structure/{id}/employees                назначить сотрудника
GET    /structure/{id}/employees
DELETE /structure/{id}/positions/{position_id}/employees/{user_id}
```

**tasks_service** — `/api/v1/companies/{company_id}`

```
POST   /tasks                          создать задачу
GET    /tasks                          список задач компании
GET    /tasks/{task_id}
PATCH  /tasks/{task_id}
PATCH  /tasks/{task_id}/change_status   смена статуса (публикует task.status_changed)
DELETE /tasks/{task_id}                 мягкое удаление
```

## Тесты

Интеграционные тесты на HTTP-ручки, тесты Kafka-обработчиков (включая идемпотентность и компенсации) и тесты саги регистрации.

Каждому сервису нужен `config/.env.test` с `DATABASE_URL` на отдельную тестовую базу. Запуск из корня сервиса:

```bash
cd auth_service && poetry run pytest
cd org_service && poetry run pytest
cd tasks_service && poetry run pytest
```
