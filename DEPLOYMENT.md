# 🚀 Развертывание Mayan EDMS

## Быстрое развертывание на новой машине

### Предварительные требования
- Windows 10/11 Pro или выше
- Минимум 4GB RAM
- Минимум 10GB свободного места
- Включена виртуализация в BIOS

### Шаг 1: Клонирование проекта

```bash
# В PowerShell или командной строке
cd C:\Users\%USERNAME%\PycharmProjects
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> Prime-EDMS
cd Prime-EDMS
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
