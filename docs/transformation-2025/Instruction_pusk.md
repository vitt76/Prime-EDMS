# 🚀 Руководство по запуску системы DAM (Prime-EDMS)

**Версия:** 1.2
**Дата:** 03 декабря 2025
**Автор:** Senior DevOps Engineer & Technical Writer

---

## 📋 Описание

Это руководство объясняет, как развернуть и запустить систему **DAM (Digital Asset Management) Prime-EDMS** в гибридной конфигурации:

- **Backend:** Django в Docker контейнерах
- **Frontend:** Vue 3 через Vite (нативно)
- **Инфраструктура:** PostgreSQL, Redis, RabbitMQ (в Docker)
- **Платформа:** Ubuntu 22.04 / Windows Subsystem for Linux (WSL 2)

---

## 🔧 Предварительные требования

### Обязательные компоненты

#### 1. Ubuntu / WSL 2
```bash
# Проверить версию Ubuntu
lsb_release -a
# Должно быть Ubuntu 22.04 или выше
```

#### 2. Docker и Docker Compose
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Проверить установку
docker --version          # 24.0+
docker compose version    # 2.0+
```

#### 3. Node.js 20+
```bash
# Установка Node.js через NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Проверить установку
node --version    # v20.0.0+
npm --version     # 10.0.0+
```

#### 4. Git
```bash
sudo apt-get install git
git --version    # 2.34+
```

#### 5. Python 3.9+ (для некоторых утилит)
```bash
python3 --version    # 3.9+
```

---

## 📦 Шаг 1: Настройка Backend (Django + Docker)

### 1.1 Клонирование репозитория

```bash
# Клонировать проект
git clone https://github.com/your-org/prime-edms.git
cd prime-edms

# Проверить содержимое
ls -la
# Должен быть: docker-compose.yml, app.env, config.yml, mayan/, frontend/
```

### 1.2 Настройка переменных окружения

```bash
# Скопировать файл с переменными окружения
cp app.env app.env.local

# Отредактировать app.env.local (если нужно изменить значения по умолчанию)
nano app.env.local

# Важные переменные (уже настроены по умолчанию):
# - S3 хранилище (Beget): MAYAN_STORAGE_S3_*
# - База данных: MAYAN_DATABASE_PASSWORD=mayandbpass
# - Redis: MAYAN_REDIS_PASSWORD=mayanredispassword
# - RabbitMQ: MAYAN_RABBITMQ_PASSWORD=mayanrabbitpass
```

### 1.3 Запуск инфраструктуры

```bash
# Запустить все сервисы (PostgreSQL, Redis, RabbitMQ, Django)
docker compose up -d

# Проверить статус контейнеров
docker compose ps

# Должен показать:
# prime-edms_postgresql_1   Up (healthy)
# prime-edms_redis_1        Up (healthy)
# prime-edms_rabbitmq_1     Up (healthy)
# prime-edms_app_1          Up (healthy)
```

### 1.4 Первоначальная настройка базы данных

```bash
# Подождать пока контейнеры запустятся (1-2 минуты)
# Mayan EDMS автоматически создаст суперпользователя через систему autoadmin

# Выполнить миграции и настройки
docker compose exec app mayan-edms.py initialsetup

# Или пошагово:
docker compose exec app mayan-edms.py migrate
docker compose exec app mayan-edms.py collectstatic --noinput
```

📋 **Автоматические учетные данные Mayan EDMS:**

**В данной конфигурации используются фиксированные значения из docker-compose.yml:**
- **Username:** admin
- **Password:** admin123
- **Email:** admin@localhost

**Как работает система autoadmin:**
1. При выполнении `mayan-edms.py initialsetup` вызывается команда `autoadmin_create`
2. Создается суперпользователь с данными из настроек `MAYAN_AUTOADMIN_*`
3. Данные сохраняются в модель `AutoAdminSingleton` для отображения на странице логина
4. При первом входе и смене пароля информация автоматически скрывается

⚠️ **Важно о паролях:**
- В данной конфигурации пароль **фиксированный** (admin123)
- При пересборке контейнеров без очистки volumes пароль **сохраняется**
- Только при полной очистке БД (`docker compose down -v`) создается новый аккаунт

**Если пароль не работает:**
```bash
# Проверить статус autoadmin
docker compose exec app mayan-edms.py shell -c "from mayan.apps.autoadmin.models import AutoAdminSingleton; print(AutoAdminSingleton.objects.first())"

# Или проверить логи создания пользователя
docker compose logs app | grep -i "auto.*admin\|superuser"
```

### 1.5 Проверка работы Backend

```bash
# Проверить доступ к Django admin
curl http://localhost:8080/admin/

# Должен вернуть HTML страницу логина

# Проверить API
curl http://localhost:8080/api/v4/

# Должен вернуть JSON с API информацией
```

---

## 🎨 Шаг 2: Настройка Frontend (Vue 3 + Vite)

### 2.1 Установка зависимостей

```bash
# Перейти в директорию frontend
cd frontend

# Установить зависимости
npm install

# Проверить установку
npm list --depth=0
```

### 2.2 Настройка переменных окружения

```bash
# Создать файл с переменными окружения
cp .env.example .env.local

# Проверить/отредактировать .env.local
cat .env.local

# Должен содержать:
# VITE_API_URL=http://localhost:8080
# VITE_USE_REAL_API=true
# (другие переменные по умолчанию)
```

### 2.3 Запуск development сервера

```bash
# Запустить Vite dev server
npm run dev

# Должен показать:
# VITE v5.4.11  ready in 1234 ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: http://0.0.0.0:5173/
# ➜  press h to show help
```

---

## ✅ Шаг 3: Проверка работы системы

### 3.1 Frontend доступен

```bash
# Открыть в браузере
firefox http://localhost:5173/

# Или через curl
curl http://localhost:5173/

# Должен вернуть HTML страницу Vue приложения
```

### 3.2 Backend API работает

```bash
# Проверить API endpoints
curl http://localhost:8080/api/v4/documents/

# Должен вернуть JSON (даже если пустой массив)

# Проверить Django admin
curl http://localhost:8080/admin/
# Должен вернуть страницу логина
```

### 3.3 Полная интеграция

```bash
# 1. Открыть frontend: http://localhost:5173/
# 2. Попробовать войти с учетными данными autoadmin:
#    - Username: admin
#    - Password: admin123 (фиксированный в docker-compose.yml)
#    - Email: admin@localhost
# 3. После входа должны загрузиться документы
# 4. Попробовать загрузить файл
# 5. Проверить просмотр документов

# 📋 Данные autoadmin также отображаются на странице Django admin:
# Откройте http://localhost:8080/admin/ в браузере
# В правом верхнем углу увидите блок с учетными данными
```

🔍 **Как работает Mayan EDMS autoadmin:**
- При первом запуске создается суперпользователь через `mayan.apps.autoadmin`
- Данные хранятся в модели `AutoAdminSingleton`
- Отображаются на странице логина Django admin
- При изменении пароля информация автоматически скрывается

---

## 🔧 Устранение неисправностей

### Проблема: "500 Internal Server Error"

```bash
# Проверить логи контейнера
docker compose logs app

# Проверить базу данных
docker compose exec postgresql psql -U mayan -d mayan -c "SELECT * FROM django_migrations LIMIT 5;"

# Перезапустить с пересозданием
docker compose down
docker compose up -d --build
```

### Проблема: "CORS Error" в браузере

```bash
# Проверить настройки CORS в backend
# Проверить VITE_API_URL в frontend/.env.local
cat frontend/.env.local

# Перезапустить frontend
cd frontend && npm run dev
```

### Проблема: Frontend не может подключиться к API

```bash
# Проверить, что backend работает
curl http://localhost:8080/api/v4/

# Проверить прокси в Vite
# Проверить firewall (если Ubuntu desktop)
sudo ufw status
sudo ufw allow 5173
sudo ufw allow 8080
```

### Проблема: RabbitMQ не запускается

```bash
# Проверить логи RabbitMQ
docker compose logs rabbitmq

# Очистить volumes и перезапустить
docker compose down -v
docker compose up -d rabbitmq
```

### Как перезапустить Celery workers

```bash
# Остановить workers
docker compose exec app supervisorctl stop all

# Запустить workers
docker compose exec app supervisorctl start all

# Проверить статус
docker compose exec app supervisorctl status
```

### Как посмотреть логи всех сервисов

```bash
# Логи всех контейнеров
docker compose logs

# Логи конкретного сервиса
docker compose logs app
docker compose logs postgresql
docker compose logs redis
docker compose logs rabbitmq

# Следить за логами в реальном времени
docker compose logs -f app
```

### Проблема: Не удается войти с паролем admin/admin123

```bash
# 1. Проверить статус autoadmin в базе данных
docker compose exec app mayan-edms.py shell -c "
from mayan.apps.autoadmin.models import AutoAdminSingleton
try:
    admin = AutoAdminSingleton.objects.first()
    print(f'Username: {admin.account.username}')
    print(f'Email: {admin.account.email}')
    print(f'Password: {admin.password}')
except:
    print('AutoAdmin не создан')
"

# 2. Если AutoAdmin не существует, пересоздать
docker compose exec app mayan-edms.py autoadmin_create

# 3. Проверить логи создания пользователя
docker compose logs app | grep -i "auto.*admin\|superuser\|admin"

# 4. Если проблема persists, сбросить БД
docker compose down -v
docker compose up -d
docker compose exec app mayan-edms.py initialsetup
```

### Как остановить и очистить систему

```bash
# Остановить все сервисы
docker compose down

# Остановить и удалить volumes (данные БД + сброс паролей)
docker compose down -v

# Полная очистка
docker system prune -a
```

⚠️ **Предупреждение:** Команда `docker compose down -v` **удаляет все данные базы данных**, включая пользователей и документы. После этого система вернется к первоначальному состоянию с автоматически сгенерированным паролем.

---

## 📊 Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   Vue 3 + Vite  │    │   Django        │
│   localhost:5173│◄──►│   localhost:8080│
│                 │    │                 │
│ - SPA Interface │    │ - REST API v4   │
│ - Asset Gallery │    │ - Document Mgmt │
│ - Upload Forms  │    │ - AI Analysis   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Infrastructure│    │   Storage       │
│   Docker        │    │   S3 (Beget)    │
│                 │    │                 │
│ PostgreSQL      │    │ - Files         │
│ Redis           │    │ - Thumbnails    │
│ RabbitMQ        │    │ - Previews      │
└─────────────────┘    └─────────────────┘
```

### Сервисы и порты

| Сервис | Порт | Описание |
|--------|------|----------|
| **Frontend (Vite)** | 5173 | Vue 3 development server |
| **Backend (Django)** | 8080 | Django application |
| **PostgreSQL** | - | База данных (внутри Docker) |
| **Redis** | - | Кеш и сессии (внутри Docker) |
| **RabbitMQ** | - | Очереди задач (внутри Docker) |

### 🔐 Система учетных данных Mayan EDMS

**Как работает autoadmin:**

1. **Команда установки:** `mayan-edms.py initialsetup` вызывает `autoadmin_create`
2. **Создание пользователя:** `mayan.apps.autoadmin` создает суперпользователя с настройками из `docker-compose.yml`:
   - `MAYAN_AUTOADMIN_USERNAME: "admin"`
   - `MAYAN_AUTOADMIN_PASSWORD: "admin123"`
   - `MAYAN_AUTOADMIN_EMAIL: "admin@localhost"`
3. **Хранение данных:** Информация сохраняется в модель `AutoAdminSingleton`
4. **Отображение:** Данные показываются на странице Django admin (`/admin/`)
5. **Автоскрытие:** При первом входе или смене пароля информация исчезает

**Файлы системы autoadmin:**
- `mayan/apps/autoadmin/management/commands/autoadmin_create.py` - команда создания
- `mayan/apps/autoadmin/models.py` - модель хранения данных
- `mayan/apps/autoadmin/templates/autoadmin/credentials.html` - шаблон отображения

---

## 🚀 Быстрый старт (для опытных пользователей)

```bash
# 1. Клонировать и настроить
git clone <repo> && cd prime-edms
cp app.env app.env.local

# 2. Запустить backend
docker compose up -d

# 3. Настроить базу данных (автогенерация admin/admin123)
docker compose exec app mayan-edms.py initialsetup

# 4. Запустить frontend
cd frontend && npm install && npm run dev

# 5. Открыть http://localhost:5173/
# Авторизация: admin / admin123 (фиксированный в docker-compose.yml)
```

📋 **Учетные данные autoadmin:**
- **Username:** admin
- **Password:** admin123 (фиксированный в данной конфигурации)
- **Email:** admin@localhost
- **Система:** Mayan EDMS autoadmin (автоматическое создание при `initialsetup`)

**Если возникли проблемы с входом:**
```bash
# Проверить статус autoadmin
docker compose exec app mayan-edms.py shell -c "
from mayan.apps.autoadmin.models import AutoAdminSingleton
admin = AutoAdminSingleton.objects.first()
print(f'Login: {admin.account.username}/{admin.password}')
"
```

---

## 📞 Поддержка

Если возникли проблемы:

1. **Проверить логи:** `docker compose logs`
2. **Проверить статус сервисов:** `docker compose ps`
3. **Проверить переменные окружения**
4. **Очистить и перезапустить:** `docker compose down -v && docker compose up -d`

**Контакты:**
- Техническая поддержка: support@yourcompany.com
- Документация: docs/transformation-2025/
- Mayan EDMS: https://docs.mayan-edms.com/

---

*Это руководство написано для junior разработчиков. Если вы опытный инженер, используйте раздел "Быстрый старт".*
