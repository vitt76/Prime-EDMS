# 🚀 Установка Mayan EDMS с расширением converter_pipeline_extension

## Быстрая установка на Ubuntu

### 1. Настройка системы
```bash
# Установка Docker и зависимостей
sudo bash ubuntu-setup.sh

# Перезайдите в систему для применения группы docker
# logout и login, или: newgrp docker
```

### 2. Подготовка проекта
```bash
# Перейдите в директорию проекта
cd ~/mayan-edms

# Подготовьте проект
./ubuntu-prepare.sh
```

### 3. Запуск Mayan EDMS
```bash
# Запустите систему
./ubuntu-start.sh start

# Или для управления:
./ubuntu-start.sh status   # статус
./ubuntu-start.sh logs     # логи
./ubuntu-start.sh stop     # остановка
./ubuntu-start.sh restart  # перезапуск
```

## Использование Makefile

```bash
# Настройка Ubuntu
make ubuntu-setup

# Подготовка проекта
make ubuntu-prepare

# Управление
make ubuntu-start  # показать справку по командам
```

## Что делает автоматизация

### ubuntu-setup.sh
- ✅ Устанавливает Docker и Docker Compose
- ✅ Устанавливает FFmpeg, Python PIL, ReportLab
- ✅ Настраивает Docker daemon
- ✅ Добавляет пользователя в группу docker

### ubuntu-prepare.sh
- ✅ Создает `config.yml` с настройками расширения
- ✅ Создает `app.env` с переменными окружения
- ✅ Создает кастомный Docker образ с расширениями
- ✅ Проверяет наличие всех необходимых файлов

### ubuntu-start.sh
- ✅ Запускает все сервисы через docker-compose
- ✅ Ожидает готовности PostgreSQL, Redis, RabbitMQ
- ✅ Проверяет успешный запуск Mayan EDMS
- ✅ Предоставляет команды управления

## Структура проекта

```
mayan-edms/
├── docker-compose.yml      # Конфигурация сервисов
├── Dockerfile.app          # Кастомный образ с расширениями
├── config.yml             # Конфигурация Mayan EDMS
├── app.env                # Переменные окружения
├── ubuntu-setup.sh        # Настройка системы
├── ubuntu-prepare.sh      # Подготовка проекта
├── ubuntu-start.sh        # Управление сервисом
├── mayan/                 # Исходный код Mayan EDMS
└── mayan/apps/converter_pipeline_extension/  # Наше расширение
```

## Проверка установки

После запуска проверьте:
- 🌐 **http://localhost** - веб-интерфейс Mayan EDMS
- 🔧 Расширение `converter_pipeline_extension` активно
- 📁 Поддержка конвертации: JPEG, PNG, TIFF, PDF, MP4→изображения

## Устранение проблем

### Приложение не запускается
```bash
# Проверьте логи
./ubuntu-start.sh logs

# Проверьте статус сервисов
./ubuntu-start.sh status

# Перезапустите
./ubuntu-start.sh restart
```

### Docker образ не найден
```bash
# Пересоберите образ
./ubuntu-prepare.sh
```

### Проблемы с зависимостями
```bash
# Проверьте установку
apt list --installed | grep -E "(ffmpeg|python3-pil|python3-reportlab)"
```

## 🎉 Готово!

Теперь у вас полностью автоматизированная установка Mayan EDMS с поддержкой конвертации мультимедиа файлов!
