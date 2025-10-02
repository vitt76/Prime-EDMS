#!/bin/bash

# Скрипт автоматической установки Mayan EDMS в WSL2
# Запускать с правами root или через sudo

set -e

echo "🚀 Начинаем установку Mayan EDMS в WSL2..."

# Проверка дистрибутива
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "❌ Этот скрипт предназначен только для Ubuntu"
    exit 1
fi

echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

echo "🐳 Установка Docker..."

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
echo "🔄 Запуск Docker daemon..."
sudo systemctl enable docker
sudo systemctl start docker

# Добавление пользователя в группу docker (требуется перезапуск сессии)
sudo usermod -aG docker $USER

echo "🐰 Установка Docker Compose..."
sudo apt install -y docker-compose

# Остановка конфликтующих сервисов
echo "🛑 Остановка конфликтующих сервисов..."
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl disable apache2 2>/dev/null || true

echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Перезапустите WSL2: wsl --shutdown && wsl"
echo "2. Перейдите в директорию проекта"
echo "3. Запустите: docker-compose -f docker-compose.simple.yml up -d"
echo "4. Откройте http://localhost в браузере"
echo ""
echo "⚠️  Важно: После перезапуска WSL2 снова перейдите в директорию проекта!"
