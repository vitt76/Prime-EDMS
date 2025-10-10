# Mayan EDMS - Система Управления Электронными Документами

[![Mayan EDMS](https://img.shields.io/badge/Mayan_EDMS-4.3.1-orange)](https://www.mayan-edms.com/)

Полнофункциональная система управления электронными документами на базе Mayan EDMS для Ubuntu.

## 🚀 Быстрый старт

### 📋 Системные требования
- **ОС**: Ubuntu 20.04+
- **RAM**: Минимум 4GB (рекомендуется 8GB+)
- **Диск**: Минимум 10GB свободного места
- **CPU**: 2+ ядра

### 🔧 Установка и запуск

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
   # Или используйте make: make start
   ```

5. **Откройте браузер и перейдите**: http://localhost

## 📋 Доступные скрипты

### Скрипты установки
- `ubuntu-setup.sh` - Автоматическая установка для Ubuntu

### Скрипты управления
- `ubuntu-start.sh` - Управление Mayan EDMS в Ubuntu
- `Makefile` - Команды make для автоматизации

### Скрипты безопасности
- `generate-ssl.sh` - Генерация самоподписанных SSL сертификатов
- `setup-https.sh` - Настройка HTTPS (самоподписанные или Let's Encrypt)

### Скрипты управления
- `ubuntu-start.sh` - Управление Mayan EDMS
- `Makefile` - Команды make для автоматизации

## 🔒 Настройка HTTPS

### Быстрая настройка HTTPS

#### Самоподписанный сертификат (для тестирования)

```bash
# Генерация сертификатов
./generate-ssl.sh your-domain.com

# Активация HTTPS
# Раскомментируйте строки в app.env:
# MAYAN_COMMON_SSL_CERTIFICATE: "/opt/mayan/certificates/ssl.crt"
# MAYAN_COMMON_SSL_KEY: "/opt/mayan/certificates/ssl.key"

# Перезапуск
make restart
```

#### Production сертификат (Let's Encrypt)

```bash
# Настройка Let's Encrypt
./setup-https.sh letsencrypt your-domain.com

# Перезапуск
make restart
```

### Доступ к HTTPS

- **URL**: https://your-domain.com (или https://localhost для самоподписанных)
- **Порт**: 443 (автоматически)
- **HTTP редирект**: Включается автоматически на HTTPS


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
├── app.env                      # Переменные окружения приложения
├── ubuntu-setup.sh              # Установка окружения
├── ubuntu-start.sh              # Управление сервисами
├── Makefile                     # Команды make
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

По умолчанию Mayan EDMS доступен на порту 80. Чтобы изменить порт, отредактируйте скрипт `ubuntu-start.sh`.

## 🔧 Управление

### Основные команды

```bash
make start    # Запуск всех сервисов
make stop     # Остановка всех сервисов
make restart  # Перезапуск приложения
make logs     # Просмотр логов
make status   # Статус контейнеров
```

### Управление через скрипт

```bash
./ubuntu-start.sh start   # Запуск
./ubuntu-start.sh stop    # Остановка
./ubuntu-start.sh restart # Перезапуск
./ubuntu-start.sh status  # Статус
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

### 🚨 Распространенные проблемы и решения

#### 1. **Порт 80 занят**
```bash
# Найти процесс, занимающий порт 80
sudo lsof -i :80

# Остановить Apache/Nginx если необходимо
sudo systemctl stop apache2
sudo systemctl disable apache2
```

#### 2. **Не хватает места на диске**
```bash
# Проверить использование диска
df -h

# Очистить ненужные пакеты
sudo apt autoremove
sudo apt autoclean
```

#### 3. **Проблемы с правами Docker**
```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перезайти в систему
# Или выполнить: newgrp docker
```

#### 4. **Приложение не запускается**
```bash
# Проверить статус сервисов
make status

# Посмотреть логи
make logs

# Перезапустить
make restart
```

#### 5. **База данных не отвечает**
```bash
# Проверить логи базы данных
./ubuntu-start.sh logs postgresql

# Перезапустить базу данных
./ubuntu-start.sh restart postgresql
```

### 🔧 Восстановление после сбоев

#### Полная перезагрузка
```bash
# Остановить все сервисы
make stop

# Перезапустить проект
make start
```

#### Очистка данных (ВНИМАНИЕ!)
```bash
# Это удалит все данные!
make stop
sudo rm -rf docker/mayan_data/*
sudo rm -rf docker/postgres_data/*
sudo rm -rf docker/rabbitmq_data/*
sudo rm -rf docker/redis_data/*
make start
```

### 📞 Получение помощи

Если проблема не решена:

1. **Соберите информацию**:
   ```bash
   make status
   make logs
   df -h
   free -h
   ```

2. **Создайте issue** в репозитории с:
   - Описанием проблемы
   - Логами команд выше
   - Версией Ubuntu: `lsb_release -a`

## 🔄 Конвертация медиа файлов

Проект включает расширение для автоматической конвертации медиа файлов с использованием FFmpeg и Pillow.

### ✨ Автоматическая интеграция

**Кнопка "Сконвертировать" автоматически добавляется в меню "Действия" файлов документов в Mayan EDMS.**

### 🎯 Как использовать

1. **Откройте Mayan EDMS**: `http://localhost`
2. **Перейдите к любому документу** с файлами
3. **В меню "Действия" файла** нажмите **"Сконвертировать"**
4. **Выберите желаемый формат** вывода
5. **Система автоматически** создаст новую версию документа

### 📁 Поддерживаемые форматы

#### Изображения
- **Входные**: JPEG, PNG, TIFF, BMP, GIF, WebP, RAW форматы (CR2, NEF, ARW, etc.)
- **Выходные**: PDF, JPEG, PNG, TIFF

#### Видео
- **Входные**: MP4, AVI, MOV, MKV, WebM, FLV, WMV, 3GP, MPG
- **Выходные**: MP4, WebM, AVI (с извлечением кадров и превью)

#### Документы
- **Входные**: PDF, DOC, DOCX
- **Выходные**: PDF (оптимизация и конвертация)

#### Аудио
- **Входные**: MP3, WAV, FLAC, AAC, OGG
- **Выходные**: Визуализация в виде изображений спектрограмм

### ⚙️ Технические возможности

- **Автоматическое определение** типа файла
- **Оптимизация качества** при конвертации
- **Извлечение превью** для видео файлов
- **Создание миниатюр** для всех типов файлов
- **Обработка метаданных** и EXIF данных
- **Пакетная обработка** через фоновые задачи

### 🔍 Диагностика

Если кнопка не появляется:

```bash
# Проверить загрузку расширения
make logs | grep "Converter Pipeline"

# Проверить JavaScript в браузере (F12 → Console)
# Должен появиться alert: "JavaScript загружен через context processor!"
```

### 📊 Мониторинг конвертаций

Все конвертации выполняются в фоне. Статус можно отслеживать в:
- **Логах приложения**: `make logs`
- **Celery воркерах**: через RabbitMQ Management (`http://localhost:15672`)
- **Интерфейсе Mayan EDMS**: в истории версий документа

## 📚 Дополнительные ресурсы

- [Официальная документация Mayan EDMS](https://docs.mayan-edms.com/)

## 📄 Лицензия

Проект основан на [Mayan EDMS](https://www.mayan-edms.com/) с лицензией Apache 2.0.

---

**Примечание**: Это упрощенная версия для быстрого развертывания. Для production использования настройте резервное копирование, мониторинг и безопасность.