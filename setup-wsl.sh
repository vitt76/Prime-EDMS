#!/bin/bash

# Скрипт автоматической установки Prime-EDMS в WSL2
# Запускать в Ubuntu WSL2

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🚀 Начинаем установку Prime-EDMS в WSL2..."

# Проверка WSL
if ! grep -qEi "(Microsoft|WSL)" /proc/version 2>/dev/null; then
    print_warning "Не обнаружена среда WSL. Продолжаем установку..."
fi

# Проверка прав root
if [[ $EUID -eq 0 ]]; then
   print_error "Этот скрипт нельзя запускать от root. Используйте: bash setup-wsl.sh"
   exit 1
fi

print_header "Обновление системы..."
sudo apt update && sudo apt upgrade -y

print_header "Установка Docker..."

# Проверка, установлен ли Docker
if docker --version >/dev/null 2>&1; then
    print_success "Docker уже установлен: $(docker --version)"
else
    # Установка зависимостей
    sudo apt install -y ca-certificates curl gnupg lsb-release

    # Добавление GPG ключа Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Добавление репозитория Docker
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Установка Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    print_success "Docker установлен"
fi

# Запуск Docker daemon
print_header "Запуск Docker daemon..."
sudo systemctl enable docker 2>/dev/null || true
sudo service docker start 2>/dev/null || sudo systemctl start docker 2>/dev/null || print_warning "Не удалось запустить Docker через systemctl (это нормально для WSL)"

# Добавление пользователя в группу docker
if ! groups $USER | grep -q docker; then
    print_header "Добавление пользователя в группу docker..."
    sudo usermod -aG docker $USER
    print_warning "Пользователь добавлен в группу docker. Необходимо перезапустить WSL или выполнить: newgrp docker"
else
    print_success "Пользователь уже в группе docker"
fi

# Установка Docker Compose (если не установлен)
if ! docker-compose --version >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    print_header "Установка Docker Compose..."
    sudo apt install -y docker-compose
    print_success "Docker Compose установлен"
else
    print_success "Docker Compose уже установлен"
fi

# Остановка конфликтующих сервисов
print_header "Проверка конфликтующих сервисов..."
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true
sudo systemctl disable apache2 2>/dev/null || true
sudo systemctl disable nginx 2>/dev/null || true

# Установка зависимостей для расширений
print_header "Установка зависимостей для расширений..."
sudo apt install -y ffmpeg python3-pip python3-dev build-essential python3-pil python3-reportlab git curl wget

# Установка reportlab в систему
sudo pip3 install reportlab --upgrade 2>/dev/null || print_warning "Не удалось установить reportlab (не критично)"

print_success "Установка завершена!"
echo ""
print_header "Следующие шаги:"
echo "1. Перезапустите WSL2 (в PowerShell выполните: wsl --shutdown && wsl)"
echo "   ИЛИ выполните в WSL: newgrp docker"
echo ""
echo "2. Перейдите в директорию проекта:"
echo "   cd /mnt/c/DAM/Prime-EDMS"
echo ""
echo "3. Подготовьте проект (если еще не сделано):"
echo "   ./ubuntu-prepare.sh"
echo ""
echo "4. Запустите Prime-EDMS:"
echo "   ./ubuntu-start.sh start"
echo "   или"
echo "   docker-compose -f docker-compose.yml up -d"
echo ""
echo "5. Откройте http://localhost в браузере"
echo ""
print_warning "Важно: После установки перезапустите WSL2 для применения группы docker!"

