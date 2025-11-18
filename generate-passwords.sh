#!/bin/bash

# Скрипт генерации сильных паролей для production развертывания
# Запуск: bash generate-passwords.sh

set -e

print_header() {
    echo -e "\033[0;34m🔧 $1\033[0m"
}

print_success() {
    echo -e "\033[0;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[0;31m❌ $1\033[0m"
}

echo "🔐 Генерация сильных паролей для Prime-EDMS..."

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    print_error ".env файл не найден"
    exit 1
fi

# Функция генерации сильного пароля
generate_password() {
    openssl rand -base64 24 | tr -d "=+/" | cut -c1-32
}

# Генерируем новые пароли
DB_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
RABBITMQ_PASSWORD=$(generate_password)
ELASTIC_PASSWORD=$(generate_password)

print_header "Генерация паролей..."

# Создаем backup оригинального файла
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
print_success "Создан backup файла .env"

# Обновляем пароли в .env
sed -i "s/MAYAN_DATABASE_PASSWORD=.*/MAYAN_DATABASE_PASSWORD=${DB_PASSWORD}/" .env
sed -i "s/MAYAN_REDIS_PASSWORD=.*/MAYAN_REDIS_PASSWORD=${REDIS_PASSWORD}/" .env
sed -i "s/MAYAN_RABBITMQ_PASSWORD=.*/MAYAN_RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}/" .env
sed -i "s/MAYAN_ELASTICSEARCH_PASSWORD=.*/MAYAN_ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}/" .env

print_success "Пароли обновлены в .env файле"

# Выводим сгенерированные пароли для справки
echo ""
print_header "Сгенерированные пароли (сохраните их!):"
echo "PostgreSQL: ${DB_PASSWORD}"
echo "Redis:      ${REDIS_PASSWORD}"
echo "RabbitMQ:   ${RABBITMQ_PASSWORD}"
echo "Elasticsearch: ${ELASTIC_PASSWORD}"
echo ""

print_warning "ВАЖНО: Эти пароли сохранены в .env файле"
print_warning "Для production deployment замените их на свои значения"
print_success "Пароли успешно сгенерированы!"

echo ""
echo "📋 Следующие шаги:"
echo "1. Проверьте .env файл: cat .env"
echo "2. Сохраните пароли в безопасном месте"
echo "3. Для production замените на свои пароли"
echo "4. Запустите подготовку: ./ubuntu-prepare.sh"
