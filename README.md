# Mayan EDMS - Система Управления Электронными Документами

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![WSL2](https://img.shields.io/badge/WSL2-Compatible-green)](https://docs.microsoft.com/en-us/windows/wsl/)
[![Mayan EDMS](https://img.shields.io/badge/Mayan_EDMS-4.3.1-orange)](https://www.mayan-edms.com/)

Полнофункциональная система управления электронными документами на базе Mayan EDMS, развернутая в Docker контейнерах для Windows (WSL2) и Linux (Ubuntu).

## 🚀 Быстрый старт

### Требования
- **Для Windows**: Windows 10/11 с WSL2 + Ubuntu 20.04+
- **Для Linux**: Ubuntu 20.04+ или другие дистрибутивы с systemd
- Минимум 4GB RAM
- Минимум 10GB свободного места

### Автоматическая установка

#### Вариант 1: Windows с WSL2

1. **Установите WSL2 и Ubuntu** (если не установлены):
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

2. **Запустите Ubuntu и перейдите в директорию проекта**:
   ```bash
   cd /mnt/c/Users/[YOUR_USERNAME]/PycharmProjects/Prime-EDMS
   ```

3. **Запустите скрипт автоматической установки**:
   ```bash
   # В Ubuntu WSL2
   ./setup-wsl.sh
   ```

4. **Перезагрузите WSL2**:
   ```powershell
   # В PowerShell
   wsl --shutdown && wsl
   ```

5. **Запустите Mayan EDMS**:
   ```bash
   # В Ubuntu WSL2
   make start
   # или
   ./start-mayan.sh start
   # или
   docker-compose -f docker-compose.simple.yml up -d
   ```

   ```powershell
   # В Windows PowerShell
   .\start-windows.bat start
   # или
   .\start-mayan.ps1
   ```

#### Вариант 2: Ubuntu (нативно)

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/vitt76/Prime-EDMS.git mayan-edms
   cd mayan-edms
   ```

2. **Запустите скрипт установки**:
   ```bash
   ./ubuntu-setup.sh
   ```

3. **Перезайдите в систему** или выполните:
   ```bash
   newgrp docker
   ```

4. **Запустите Mayan EDMS**:
   ```bash
   ./ubuntu-start.sh start
   ```

5. **Откройте браузер и перейдите**: http://localhost

## 📋 Доступные скрипты

### Скрипты установки
- `setup-wsl.sh` - Автоматическая установка для Windows WSL2
- `ubuntu-setup.sh` - Автоматическая установка для Ubuntu нативно

### Скрипты управления
- `start-mayan.sh` - Управление Mayan EDMS в WSL2/Linux
- `ubuntu-start.sh` - Управление Mayan EDMS в Ubuntu нативно
- `start-mayan.ps1` - Управление Mayan EDMS в Windows PowerShell
- `start-windows.bat` - Управление Mayan EDMS в Windows CMD
- `Makefile` - Команды make для автоматизации (только в WSL2/Ubuntu)

### Сравнение подходов

| Платформа | Скрипт установки | Скрипт управления | Особенности |
|-----------|----------------|-------------------|-------------|
| **Windows + WSL2** | `setup-wsl.sh` | `start-mayan.sh`, `make`, `start-mayan.ps1`, `start-windows.bat` | Перезапуск WSL2 после установки |
| **Ubuntu нативно** | `ubuntu-setup.sh` | `ubuntu-start.sh`, `make` | Максимальная производительность |
| **Windows (только)** | `setup-windows.bat` | `start-windows.bat`, `start-mayan.ps1` | Через WSL2 в фоне |

## 📋 Ручная установка

### Вариант A: Установка в WSL2 (Windows)

#### Шаг 1: Установка Docker в WSL2

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y ca-certificates curl gnupg lsb-release

# Добавление GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Запуск Docker daemon
sudo systemctl enable docker
sudo systemctl start docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

#### Шаг 2: Запуск Mayan EDMS в WSL2

```bash
# Переход в директорию проекта
cd /mnt/c/Users/[YOUR_USERNAME]/PycharmProjects/Prime-EDMS

# Перезапуск WSL2 для применения группы docker
# В PowerShell: wsl --shutdown && wsl

# Запуск сервисов
docker-compose -f docker-compose.simple.yml up -d

# Проверка статуса
docker ps
```

### Вариант B: Установка в Ubuntu (нативно)

#### Шаг 1: Установка Docker в Ubuntu

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y ca-certificates curl gnupg lsb-release

# Добавление GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Запуск Docker daemon
sudo systemctl enable docker
sudo systemctl start docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезаход в систему
newgrp docker
```

#### Шаг 2: Запуск Mayan EDMS в Ubuntu

```bash
# Переход в директорию проекта
cd ~/mayan-edms

# Запуск сервисов
docker-compose -f docker-compose.simple.yml up -d

# Проверка статуса
docker ps
```

### Шаг 3: Доступ к системе

- **URL**: http://localhost
- **Первоначальная настройка**: Следуйте инструкциям в веб-интерфейсе

## 🏗️ Архитектура

```
Mayan EDMS Stack:
├── PostgreSQL (База данных)
├── Redis (Кэш и брокер задач)
├── RabbitMQ (Очередь сообщений)
└── Mayan EDMS (Основное приложение)
```

### Сервисы:
- **PostgreSQL**: Хранение данных
- **Redis**: Кэширование и управление блокировками
- **RabbitMQ**: Очередь фоновых задач
- **Mayan EDMS**: Веб-приложение на Django + Gunicorn

## 📁 Структура проекта

```
Prime-EDMS/
├── docker-compose.simple.yml    # Конфигурация Docker Compose
├── app.env                      # Переменные окружения приложения
├── setup-wsl.sh                 # Скрипт установки для WSL2
├── start-mayan.sh               # Скрипт запуска (Windows)
├── README.md                    # Документация
└── .gitignore                   # Исключаемые файлы
```

## ⚙️ Настройка

### Переменные окружения

Создайте файл `app.env` с настройками:

```bash
# База данных
MAYAN_DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayandbpass','USER':'mayan','HOST':'postgresql'}}

# Redis (кэш)
MAYAN_CELERY_BROKER_URL=amqp://mayan:mayanrabbitpass@rabbitmq:5672/mayan
MAYAN_CELERY_RESULT_BACKEND=redis://:mayanredispassword@redis:6379/1

# Блокировщик
MAYAN_LOCK_MANAGER_BACKEND=mayan.apps.lock_manager.backends.redis_lock.RedisLock
MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS={'redis_url':'redis://:mayanredispassword@redis:6379/2'}
```

### Изменение порта

По умолчанию Mayan EDMS доступен на порту 80. Чтобы изменить порт:

```yaml
# В docker-compose.simple.yml измените:
ports:
  - "8080:8000"  # Вместо "80:8000"
```

## 🔧 Управление

### Основные команды

```bash
# Запуск всех сервисов
docker-compose -f docker-compose.simple.yml up -d

# Остановка всех сервисов
docker-compose -f docker-compose.simple.yml down

# Просмотр логов
docker-compose -f docker-compose.simple.yml logs -f

# Перезапуск приложения
docker-compose -f docker-compose.simple.yml restart app

# Просмотр статуса контейнеров
docker ps
```

### Очистка данных

```bash
# Остановка и удаление всех контейнеров
docker-compose -f docker-compose.simple.yml down

# Удаление volumes (ВНИМАНИЕ: удалятся все данные!)
docker volume rm $(docker volume ls -q | grep prime-edms)

# Полная очистка
docker system prune -a --volumes
```

## 🔒 Безопасность

- Все пароли заданы по умолчанию для демонстрации
- **В production измените все пароли в `app.env`**
- Используйте HTTPS в production окружении
- Настройте firewall и ограничьте доступ

## 📊 Мониторинг

### Проверка работоспособности

```bash
# Статус всех контейнеров
docker ps

# Логи приложения
docker logs prime-edms_app_1

# Использование ресурсов
docker stats
```

### Доступ к сервисам

- **Mayan EDMS**: http://localhost
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **PostgreSQL**: localhost:5432 (mayan/mayandbpass)

## 🚀 Возможности Mayan EDMS

- ✅ Управление документами
- 🔍 Полнотекстовый поиск
- 📄 OCR распознавание текста
- 🏷️ Система тегов и метаданных
- 👥 Управление пользователями и правами
- 🔄 Рабочие процессы
- 📊 Статистика и отчеты
- 🔗 REST API
- 📱 Веб-интерфейс

## 🐛 Устранение проблем

### Порт 80 занят
```bash
# Найти процесс, занимающий порт 80
sudo lsof -i :80

# Остановить Apache/Nginx если необходимо
sudo systemctl stop apache2
```

### Docker не запускается
```bash
# Проверить статус Docker daemon
sudo systemctl status docker

# Перезапустить Docker
sudo systemctl restart docker
```

### Ошибки сети
```bash
# Пересоздать сеть
docker-compose -f docker-compose.simple.yml down
docker network rm prime-edms_mayan
docker-compose -f docker-compose.simple.yml up -d
```

## 📚 Дополнительные ресурсы

- [Официальная документация Mayan EDMS](https://docs.mayan-edms.com/)
- [Docker документация](https://docs.docker.com/)
- [WSL2 документация](https://docs.microsoft.com/en-us/windows/wsl/)

## 📄 Лицензия

Проект основан на [Mayan EDMS](https://www.mayan-edms.com/) с лицензией Apache 2.0.

---

**Примечание**: Это упрощенная версия для быстрого развертывания. Для production использования настройте резервное копирование, мониторинг и безопасность.