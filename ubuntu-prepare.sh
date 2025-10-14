#!/bin/bash

# Скрипт подготовки проекта Mayan EDMS с расширением converter_pipeline_extension
# Запускать после ubuntu-setup.sh

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

echo "🚀 Подготовка проекта Mayan EDMS с converter_pipeline_extension..."

# Проверка Docker
if ! docker --version >/dev/null 2>&1; then
    print_error "Docker не установлен. Запустите: bash ubuntu-setup.sh"
    exit 1
fi

if ! docker-compose --version >/dev/null 2>&1; then
    print_error "Docker Compose не установлен"
    exit 1
fi

# Проверка группы docker
if ! groups $USER | grep -q docker; then
    print_warning "Пользователь не в группе docker. Выполните: newgrp docker"
    exit 1
fi

# Проверка наличия необходимых файлов
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml не найден. Убедитесь что находитесь в директории проекта."
    exit 1
fi

print_header "Создание конфигурационных файлов..."

# Создание config.yml если не существует
if [ ! -f "config.yml" ]; then
    print_header "Создание config.yml..."
    cat > config.yml << 'EOF'
common:
  extra_apps:
    - mayan.apps.converter_pipeline_extension
EOF
    print_success "config.yml создан"
else
    print_success "config.yml уже существует"
fi

# Создание app.env если не существует
if [ ! -f "app.env" ]; then
    print_header "Создание app.env..."
    cat > app.env << 'EOF'
# Mayan EDMS Environment Variables
MAYAN_SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)
MAYAN_DEBUG=False
EOF
    print_success "app.env создан"
else
    print_success "app.env уже существует"
fi

# Проверка наличия расширения
if [ ! -d "mayan/apps/converter_pipeline_extension" ]; then
    print_error "Расширение converter_pipeline_extension не найдено в mayan/apps/"
    print_warning "Убедитесь, что весь проект скопирован"
    exit 1
fi

print_header "Подготовка Docker образов..."

# Создание базового образа с зависимостями
print_header "Создание Docker образа с расширениями..."
if [ ! -f "Dockerfile.app" ]; then
    cat > Dockerfile.app << 'EOF'
FROM mayanedms/mayanedms:s4.3

# Установка системных зависимостей для расширения
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        python3-pil \
        python3-reportlab \
        python3-pip \
        python3-dev \
        build-essential && \
    pip3 install reportlab --upgrade && \
    rm -rf /var/lib/apt/lists/*

# Копирование расширения
COPY mayan/apps/converter_pipeline_extension /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/converter_pipeline_extension

EOF
    print_success "Dockerfile.app создан"
fi

print_header "Сборка Docker образа..."
docker build -f Dockerfile.app -t prime-edms_app:latest .
print_success "Docker образ собран"

print_success "Подготовка проекта завершена!"
echo ""
echo "🚀 Теперь можно запускать Mayan EDMS:"
echo "   ./ubuntu-start.sh start"
echo ""
echo "📋 После запуска откройте http://localhost в браузере"
echo "🔧 Расширение converter_pipeline_extension будет активно"
