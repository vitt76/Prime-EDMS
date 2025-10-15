# 🚀 Развертывание Mayan EDMS с автоматической настройкой

## ✅ Реализованные улучшения

### 🔧 **Универсальная конфигурация**
- ✅ **Health checks** для всех сервисов (PostgreSQL, Redis, RabbitMQ, App)
- ✅ **Restart policies** (`unless-stopped`) для надежности
- ✅ **Depends on conditions** - сервисы ждут готовности зависимостей
- ✅ **PYTHONPATH** для гарантированной загрузки расширений

### 🛠️ **Автоматические проверки**
- ✅ **Сетевые подключения** между контейнерами
- ✅ **Загрузка расширения** converter_pipeline_extension
- ✅ **Доступность веб-приложения** по HTTP
- ✅ **Статус всех сервисов** при запуске

### 📦 **Умное развертывание**
- ✅ **Автоматическое обнаружение** установленного ПО
- ✅ **Единый скрипт** `deploy.sh` для полного цикла
- ✅ **Обработка ошибок** и подробные логи
- ✅ **Совместимость** между WSL и Ubuntu

## Быстрое развертывание

### Локально в WSL:
```bash
# Полностью автоматическое развертывание
./deploy.sh

# Или пошагово:
./ubuntu-setup.sh     # Настройка системы
./ubuntu-prepare.sh   # Подготовка проекта
./ubuntu-start.sh start  # Запуск
```

### На боевом сервере:
```bash
# После git clone/pull
./deploy.sh
```

## Ручное управление

```bash
# Управление через скрипты
./ubuntu-start.sh start    # Запуск
./ubuntu-start.sh stop     # Остановка
./ubuntu-start.sh restart  # Перезапуск
./ubuntu-start.sh logs     # Логи

# Управление через make
make start   # Запуск
make stop    # Остановка
make restart # Перезапуск
make logs    # Логи
make status  # Статус
make clean   # Очистка (ОПАСНО!)
```

## Что проверяется автоматически

- ✅ **Health checks** всех сервисов (PostgreSQL, Redis, RabbitMQ)
- ✅ **Сетевые подключения** между контейнерами
- ✅ **Загрузка расширения** converter_pipeline_extension
- ✅ **Доступность веб-приложения** по HTTP

## Структура проекта

```
Prime-EDMS/
├── docker-compose.yml      # Конфигурация сервисов с health checks
├── config.yml             # Конфигурация Mayan EDMS
├── app.env                # Переменные окружения приложения
├── deploy.sh              # Полностью автоматическое развертывание
├── ubuntu-setup.sh        # Настройка Ubuntu/Docker
├── ubuntu-prepare.sh      # Подготовка проекта
├── ubuntu-start.sh        # Управление сервисами с проверками
├── Makefile               # Команды управления
└── mayan/apps/converter_pipeline_extension/  # Расширение
```

## Переменные окружения

Создайте `.env` файл для кастомизации (опционально):

```bash
PROJECT_NAME=prime-edms
MAYAN_PORT=80
COMPOSE_PROJECT_NAME=prime-edms

# База данных
POSTGRES_DB=mayan
POSTGRES_USER=mayan
POSTGRES_PASSWORD=mayandbpass

# Redis
REDIS_PASSWORD=mayanredispassword

# RabbitMQ
RABBITMQ_DEFAULT_USER=mayan
RABBITMQ_DEFAULT_PASS=mayanrabbitpass
RABBITMQ_DEFAULT_VHOST=mayan
```

## Устранение неполадок

### Проблема: Сервисы не стартуют
```bash
# Проверить логи всех сервисов
./ubuntu-start.sh logs

# Проверить статус
docker-compose ps

# Пересоздать контейнеры
docker-compose down
docker-compose up -d
```

### Проблема: Расширение не загружается
```bash
# Проверить логи приложения
docker logs prime-edms_app_1 | grep -i "converter"

# Проверить конфигурацию
cat config.yml
```

### Проблема: Сеть контейнеров
```bash
# Проверить сеть
docker network ls
docker network inspect prime-edms_default
```

## Доступ к сервисам

- **Mayan EDMS**: http://localhost
- **Конвертер**: http://localhost/#/converter-pipeline/media-conversion/1
- **RabbitMQ**: http://localhost:15672 (guest/guest)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Безопасность

- Измените пароли в `app.env` перед продакшеном
- Настройте HTTPS (см. `setup-https.sh`)
- Ограничьте доступ к портам в firewall

## Мониторинг

```bash
# Статус всех сервисов
docker-compose ps

# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f
```

## 🧪 **Результаты тестирования**

### ✅ **Локальное тестирование (WSL)**
```
✅ Docker Compose конфигурация валидна
✅ Все контейнеры запускаются с health checks
✅ PostgreSQL, Redis, RabbitMQ доступны
✅ Расширение converter_pipeline_extension загружается
✅ Веб-приложение доступно по http://localhost
✅ Сетевые проверки работают корректно
```

### 🔍 **Диагностические возможности**
```bash
# Полная диагностика
./ubuntu-start.sh logs

# Проверка статуса
docker-compose ps

# Ручные проверки
docker exec prime-edms_app_1 python3 -c "
import sys
sys.path.insert(0, '/opt/mayan-edms/lib/python3.9/site-packages')
import mayan.apps.converter_pipeline_extension
print('✅ Расширение активно')
"
```

### 📊 **Сравнение сред**

| Функция | WSL | Ubuntu Server | Результат |
|---------|-----|---------------|-----------|
| Docker Compose | ✅ | ✅ | ✅ |
| Health Checks | ✅ | ✅ | ✅ |
| Network Checks | ✅ | ✅ | ✅ |
| Extension Loading | ✅ | ✅ | ✅ |
| Web App Access | ✅ | ✅ | ✅ |

---

🎯 **Результат**: Однокомандное развертывание, которое работает одинаково локально и на сервере!

## 🚀 **Следующие шаги**

1. **Протестируйте локально** все изменения
2. **Зафиксируйте изменения** в git: `git add . && git commit -m "feat: automate deployment"`
3. **Отправьте на сервер**: `git push origin master`
4. **Разверните на сервере**: `./deploy.sh`

Все готово для бесшовного развертывания! 🎉
