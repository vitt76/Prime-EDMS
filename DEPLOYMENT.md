# 🚀 Развертывание Mayan EDMS

## Быстрое развертывание на новой машине

### Предварительные требования
- **Для Windows**: Windows 10/11 Pro или выше с WSL2
- **Для Linux**: Ubuntu 20.04+ или другие дистрибутивы с systemd
- Минимум 4GB RAM
- Минимум 10GB свободного места
- Включена виртуализация в BIOS (для Windows)

### Шаг 1: Клонирование проекта

#### Для Windows (WSL2):
```bash
# В Ubuntu WSL2
cd /mnt/c/Users/$USER/PycharmProjects
git clone https://github.com/vitt76/Prime-EDMS.git Prime-EDMS
cd Prime-EDMS
```

#### Для Ubuntu (нативно):
```bash
# В Ubuntu
git clone https://github.com/vitt76/Prime-EDMS.git mayan-edms
cd mayan-edms
```

### Шаг 2: Настройка WSL2

```powershell
# В PowerShell с правами администратора
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2
```

### Шаг 3: Автоматическая установка

```bash
# Запустите Ubuntu WSL2 и перейдите в директорию проекта
cd /mnt/c/Users/$USER/PycharmProjects/Prime-EDMS

# Запустите автоматическую установку
make setup
# или
./setup-wsl.sh
```

### Шаг 4: Перезапуск WSL2

```powershell
# В PowerShell
wsl --shutdown
wsl
```

### Шаг 5: Запуск Mayan EDMS

```bash
# В WSL2 Ubuntu
cd /mnt/c/Users/$USER/PycharmProjects/Prime-EDMS

# Запуск системы
make start
# или
docker-compose -f docker-compose.simple.yml up -d
```

### Шаг 6: Доступ к системе

Откройте браузер и перейдите: **http://localhost**

## 🐧 Развертывание на Ubuntu (нативно)

### Шаг 1: Установка Ubuntu

Установите Ubuntu 20.04+ на ваш сервер или виртуальную машину.

### Шаг 2: Клонирование проекта

```bash
# В Ubuntu
git clone https://github.com/vitt76/Prime-EDMS.git mayan-edms
cd mayan-edms
```

### Шаг 3: Автоматическая установка

```bash
# Запустите скрипт установки (не от root!)
./ubuntu-setup.sh
```

### Шаг 4: Перезаход в систему

```bash
# Перезайдите в систему или выполните:
newgrp docker
```

### Шаг 5: Запуск Mayan EDMS

```bash
# Запуск системы
./ubuntu-start.sh start

# Или используя make (если установлен)
make start

# Или напрямую через docker-compose
docker-compose -f docker-compose.simple.yml up -d
```

### Шаг 6: Доступ к системе

Откройте браузер и перейдите: **http://localhost**

## 💻 Развертывание на Windows (нативно)

### Шаг 1: Установка WSL2

```powershell
# В PowerShell с правами администратора
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2
restart-computer  # Перезагрузка компьютера
```

### Шаг 2: Запуск автоматической установки

```cmd
# В командной строке Windows
setup-windows.bat
```

Или вручную:

```powershell
# В PowerShell
git clone https://github.com/vitt76/Prime-EDMS.git Prime-EDMS
cd Prime-EDMS

# Запуск Ubuntu и установка
wsl --distribution Ubuntu-22.04
# В Ubuntu:
cd /mnt/c/Users/$USER/Prime-EDMS
./setup-wsl.sh
```

### Шаг 3: Запуск Mayan EDMS

```cmd
# В командной строке Windows
start-windows.bat start
```

Или в PowerShell:
```powershell
.\start-mayan.ps1
```

### Шаг 4: Доступ к системе

Откройте браузер и перейдите: **http://localhost**

## 🛠️ Альтернативные способы запуска

### Использование PowerShell скрипта (Windows)

```powershell
# В PowerShell из директории проекта
.\start-mayan.ps1              # Запуск
.\start-mayan.ps1 -Stop        # Остановка
.\start-mayan.ps1 -Restart     # Перезапуск
.\start-mayan.ps1 -Logs        # Логи
.\start-mayan.ps1 -Status      # Статус
.\start-mayan.ps1 -Clean       # Очистка данных (ОПАСНО!)
```

### Использование Makefile (WSL2/Linux)

```bash
cd /mnt/c/Users/$USER/PycharmProjects/Prime-EDMS

make help      # Справка по командам
make start     # Запуск
make stop      # Остановка
make restart   # Перезапуск
make logs      # Логи
make status    # Статус
make clean     # Очистка данных
```

### Использование скрипта Ubuntu (Ubuntu нативно)

```bash
cd ~/mayan-edms

./ubuntu-start.sh start     # Запуск
./ubuntu-start.sh stop      # Остановка
./ubuntu-start.sh restart   # Перезапуск
./ubuntu-start.sh logs      # Логи
./ubuntu-start.sh status    # Статус
./ubuntu-start.sh clean     # Очистка данных (ОПАСНО!)

# Или с make (если установлен)
make help      # Справка по командам
make start     # Запуск
make stop      # Остановка
make restart   # Перезапуск
make logs      # Логи
make status    # Статус
make clean     # Очистка данных
```

### Использование Windows скриптов (Windows)

```cmd
REM В командной строке Windows
start-windows.bat start     # Запуск
start-windows.bat stop      # Остановка
start-windows.bat restart   # Перезапуск
start-windows.bat logs      # Логи
start-windows.bat status    # Статус
start-windows.bat clean     # Очистка данных (ОПАСНО!)
```

```powershell
# В PowerShell
.\start-mayan.ps1              # Запуск
.\start-mayan.ps1 -Stop        # Остановка
.\start-mayan.ps1 -Restart     # Перезапуск
.\start-mayan.ps1 -Logs        # Логи
.\start-mayan.ps1 -Status      # Статус
.\start-mayan.ps1 -Clean       # Очистка данных (ОПАСНО!)
```

## 📚 Доступные скрипты

### Скрипты установки
- `setup-wsl.sh` - Установка для Windows WSL2
- `ubuntu-setup.sh` - Установка для Ubuntu нативно
- `setup-windows.bat` - Установка для Windows (с WSL2)

### Скрипты управления
- `start-mayan.sh` - Управление для WSL2/Linux
- `ubuntu-start.sh` - Управление для Ubuntu нативно
- `start-mayan.ps1` - Управление для Windows PowerShell
- `start-windows.bat` - Управление для Windows CMD
- `Makefile` - Команды make для Linux (только в WSL2/Ubuntu)

## 🔧 Настройка

### Изменение порта

Если порт 80 занят, измените его в `docker-compose.simple.yml`:

```yaml
services:
  app:
    ports:
      - "8080:8000"  # Измените 80 на нужный порт
```

### Кастомные настройки

Создайте файл `docker-compose.override.yml` для локальных настроек:

```yaml
version: '3.9'
services:
  app:
    environment:
      # Ваши переменные окружения
      MAYAN_SECRET_KEY: "your-secret-key"
```

### Переменные окружения

Создайте файл `local.env` для переопределения переменных:

```bash
# Пароли баз данных
MAYAN_DATABASE_PASSWORD=your_secure_db_password
MAYAN_REDIS_PASSWORD=your_secure_redis_password
MAYAN_RABBITMQ_PASSWORD=your_secure_rabbitmq_password

# Другие настройки
MAYAN_SECRET_KEY=your-secret-key
```

## 🐛 Устранение проблем

### Docker не запускается
```bash
# Проверить статус Docker
sudo systemctl status docker

# Перезапустить Docker
sudo systemctl restart docker

# Проверить логи
sudo journalctl -u docker -f
```

### Порт занят
```bash
# Найти процесс, занимающий порт
sudo lsof -i :80

# Остановить Apache/Nginx
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### Ошибки сети в контейнерах
```bash
# Пересоздать сеть
docker-compose -f docker-compose.simple.yml down
docker network rm prime-edms_mayan
docker-compose -f docker-compose.simple.yml up -d
```

### Очистка системы
```bash
# Полная очистка (удалит все данные!)
make clean
# или
docker-compose -f docker-compose.simple.yml down -v
docker system prune -a --volumes
```

## 📊 Мониторинг

### Проверка работоспособности
```bash
# Статус всех сервисов
docker ps

# Логи приложения
docker logs prime-edms_app_1

# Использование ресурсов
docker stats
```

### Доступ к сервисам
- **Mayan EDMS**: http://localhost
- **RabbitMQ Management**: http://localhost:15672 (mayan/mayanrabbitpass)
- **PostgreSQL**: localhost:5432 (mayan/mayandbpass)

## 🔒 Production настройки

Для использования в production:

1. **Измените все пароли** в `local.env`
2. **Настройте HTTPS** (добавьте reverse proxy)
3. **Настройте резервное копирование**
4. **Ограничьте доступ** firewall'ом
5. **Мониторьте логи** и метрики

## 📞 Поддержка

При проблемах:
1. Проверьте логи: `make logs`
2. Проверьте статус: `make status`
3. Перезапустите: `make restart`
4. Очистите и переустановите: `make clean && make start`

## 📝 Заметки

- Все данные хранятся в Docker volumes
- Логи автоматически ротируются
- Система автоматически перезапускается при сбоях
- Первый запуск может занять 2-3 минуты
