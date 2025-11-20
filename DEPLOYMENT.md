# 🚀 Развертывание Prime-EDMS

## 🏭 Production развертывание (Рекомендуется)

### Предварительные требования
- Ubuntu 18.04+ с 4GB+ RAM и 20GB+ места
- Домен с SSL сертификатами
- Root доступ или sudo

### Быстрое production развертывание:
```bash
# 1. Клонировать и перейти в директорию
git clone <repository> ~/prime-edms
cd ~/prime-edms

# 2. Сгенерировать сильные пароли
./generate-passwords.sh

# 3. Настроить домен в .env
echo "MAYAN_ALLOWED_HOSTS=your-domain.com,www.your-domain.com" >> .env

# 4. Запустить production развертывание
docker-compose -f docker-compose.prod.yml up -d
```

### Дополнительные production шаги:
1. **SSL сертификаты**: Настройте Let's Encrypt или добавьте свои сертификаты
2. **Reverse proxy**: Nginx или Traefik перед Mayan EDMS
3. **Firewall**: Ограничьте доступ только к портам 80/443
4. **Backup**: Настройте автоматическое резервное копирование
5. **Monitoring**: Добавьте логирование и health checks

## 🛠️ Development развертывание

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
git clone https://github.com/vitt76/Prime-EDMS.git prime-edms
cd prime-edms
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

# Запустите автоматическую установку системы
sudo bash ubuntu-setup.sh

# Перезайдите в систему или выполните
newgrp docker
```

### Шаг 4: Перезапуск WSL2

```powershell
# В PowerShell
wsl --shutdown
wsl
```

### Шаг 4: Подготовка проекта

```bash
# В Ubuntu
cd ~/prime-edms

# Подготовьте проект (создание образов, конфигурация)
./ubuntu-prepare.sh
```

### Шаг 5: Запуск Prime-EDMS

```bash
# В Ubuntu
cd ~/prime-edms

# Запуск системы
./ubuntu-start.sh start
# или напрямую через docker-compose
docker-compose -f docker-compose.yml up -d
```

### Шаг 6: Доступ к системе

Откройте браузер и перейдите: **http://localhost:8080** (порт 8080 по умолчанию, можно изменить в docker-compose.yml)

**Доступные разделы:**
- 🌐 **Главная**: http://localhost:8080
- 📁 **Публикации**: http://localhost:8080/#/distribution/publications/
- ⚙️ **Пресеты**: http://localhost:8080/#/distribution/presets/
- 👥 **Получатели**: http://localhost:8080/#/distribution/recipients/

**Расширения активны:**
- ✅ **converter_pipeline_extension**: 63+ форматов файлов
- ✅ **distribution**: рендишены + share links

## 🐧 Развертывание на Ubuntu (нативно)

### Шаг 1: Установка Ubuntu

Установите Ubuntu 20.04+ на ваш сервер или виртуальную машину.

### Шаг 2: Клонирование проекта

```bash
# В Ubuntu
git clone https://github.com/vitt76/Prime-EDMS.git prime-edms
cd prime-edms
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

### Шаг 5: Подготовка проекта

```bash
# Подготовьте проект (создание образов, конфигурация)
./ubuntu-prepare.sh
```

### Шаг 6: Запуск Prime-EDMS

```bash
# Запуск системы
./ubuntu-start.sh start

# Или используя make (если установлен)
make start

# Или напрямую через docker-compose
docker-compose -f docker-compose.yml up -d
```

### Шаг 6: Доступ к системе

Откройте браузер и перейдите: **http://localhost:8080** (порт 8080 по умолчанию, можно изменить в docker-compose.yml)

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

Откройте браузер и перейдите: **http://localhost:8080** (порт 8080 по умолчанию, можно изменить в docker-compose.yml)

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

Если порт 8080 занят, измените его в `docker-compose.yml`:

```yaml
services:
  app:
    ports:
      - "80:8000"  # Измените 8080 на нужный порт (например, 80 для стандартного HTTP)
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
- **Mayan EDMS**: http://localhost:8080 (порт можно изменить в docker-compose.yml)
- **RabbitMQ Management**: http://localhost:15672 (mayan/mayanrabbitpass) - только если порты раскомментированы в docker-compose.yml
- **PostgreSQL**: localhost:5432 (mayan/mayandbpass) - только если порты раскомментированы в docker-compose.yml

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
