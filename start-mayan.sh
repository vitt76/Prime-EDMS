#!/bin/bash

# Скрипт для запуска Mayan EDMS в WSL2

echo "Запуск Mayan EDMS..."

# Переход в директорию проекта
cd "$(dirname "$0")"

# Запуск Docker daemon (если не запущен)
sudo dockerd > /dev/null 2>&1 &
sleep 3

# Запуск сервисов
docker-compose -f docker-compose.simple.yml up -d

echo "Mayan EDMS запущен!"
echo "Веб-интерфейс доступен по адресу: http://localhost"
echo ""
echo "Управление:"
echo "  Остановить: docker-compose -f docker-compose.simple.yml down"
echo "  Просмотр логов: docker-compose -f docker-compose.simple.yml logs -f"
echo "  Статус контейнеров: docker ps"
