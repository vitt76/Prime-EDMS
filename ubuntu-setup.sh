#!/bin/bash

# Скрипт автоматической установки Mayan EDMS на Ubuntu
# Запускать с правами root или через sudo

set -e

echo "🚀 Начинаем установку Mayan EDMS на Ubuntu..."

# Проверка дистрибутива
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "❌ Этот скрипт предназначен только для Ubuntu"
    exit 1
fi

# Проверка прав root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Этот скрипт нельзя запускать от root. Используйте: bash ubuntu-setup.sh"
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

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

echo "🐰 Установка Docker Compose..."
sudo apt install -y docker-compose

# Остановка конфликтующих сервисов
echo "🛑 Остановка конфликтующих сервисов..."
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true
sudo systemctl disable apache2 2>/dev/null || true
sudo systemctl disable nginx 2>/dev/null || true

# Установка зависимостей для расширения converter_pipeline_extension
echo "📦 Установка зависимостей для converter_pipeline_extension..."
sudo apt install -y ffmpeg python3-pip python3-dev build-essential python3-pil python3-reportlab

# Установка reportlab в систему
sudo pip3 install reportlab --upgrade

# Установка дополнительных инструментов
echo "🔧 Установка дополнительных инструментов..."
sudo apt install -y git curl wget htop

echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Перезайдите в систему или выполните: newgrp docker"
echo "2. Перейдите в директорию проекта:"
echo "   cd ~/mayan-edms"
echo "3. Подготовьте проект:"
echo "   ./ubuntu-prepare.sh"
echo "4. Запустите Mayan EDMS:"
echo "   ./ubuntu-start.sh start"
echo "5. Откройте http://localhost в браузере"
echo ""
echo "⚠️  Важно: После установки перезайдите в систему для применения группы docker!"
echo ""
echo "📚 Дополнительная информация в README.md и DEPLOYMENT.md"
