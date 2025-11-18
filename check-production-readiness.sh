#!/bin/bash

# Скрипт проверки готовности проекта к production развертыванию
# Запуск: bash check-production-readiness.sh

set -e

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

echo "🔍 Проверка готовности Prime-EDMS к production развертыванию..."
echo ""

# Проверка наличия необходимых файлов
check_files() {
    print_header "Проверка файлов проекта"

    local required_files=("docker-compose.yml" "docker-compose.prod.yml" "Dockerfile.app" ".env" "config.yml" "ubuntu-setup.sh" "ubuntu-prepare.sh" "ubuntu-start.sh" "generate-passwords.sh")
    local missing_files=()

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "Все необходимые файлы присутствуют"
    else
        print_error "Отсутствуют файлы: ${missing_files[*]}"
        return 1
    fi
}

# Проверка расширений Mayan EDMS
check_extensions() {
    print_header "Проверка расширений Mayan EDMS"

    local extensions=("mayan/apps/converter_pipeline_extension" "mayan/apps/distribution" "mayan/apps/image_editor" "mayan/apps/dam")
    local missing_extensions=()

    for ext in "${extensions[@]}"; do
        if [ ! -d "$ext" ]; then
            missing_extensions+=("$ext")
        fi
    done

    if [ ${#missing_extensions[@]} -eq 0 ]; then
        print_success "Все расширения присутствуют"
    else
        print_error "Отсутствуют расширения: ${missing_extensions[*]}"
        return 1
    fi
}

# Проверка переменных окружения
check_env_vars() {
    print_header "Проверка переменных окружения"

    if [ ! -f ".env" ]; then
        print_error ".env файл не найден"
        return 1
    fi

    local weak_passwords=()
    local missing_vars=()

    # Проверка паролей
    while IFS='=' read -r key value; do
        case $key in
            MAYAN_DATABASE_PASSWORD|MAYAN_REDIS_PASSWORD|MAYAN_RABBITMQ_PASSWORD|MAYAN_ELASTICSEARCH_PASSWORD)
                if [[ "$value" == *"CHANGE_THIS_STRONG_PASSWORD"* ]] || [[ "$value" == *"mayandbpass"* ]] || [[ "$value" == *"mayanredispassword"* ]] || [[ "$value" == *"mayanrabbitpass"* ]]; then
                    weak_passwords+=("$key")
                fi
                ;;
            MAYAN_SECRET_KEY)
                if [ -z "$value" ] || [[ "$value" == *"your-secret-key"* ]]; then
                    missing_vars+=("$key")
                fi
                ;;
        esac
    done < .env

    if [ ${#weak_passwords[@]} -gt 0 ]; then
        print_warning "Найдены слабые пароли: ${weak_passwords[*]}"
        print_warning "Запустите: ./generate-passwords.sh"
    else
        print_success "Пароли выглядят безопасными"
    fi

    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_warning "Отсутствуют переменные: ${missing_vars[*]}"
    fi
}

# Проверка production настроек
check_production_settings() {
    print_header "Проверка production настроек"

    if [ ! -f "mayan/settings/production.py" ]; then
        print_error "mayan/settings/production.py не найден"
        return 1
    fi

    if grep -q "DEBUG = True" mayan/settings/production.py; then
        print_error "DEBUG = True в production настройках"
        return 1
    fi

    print_success "Production настройки корректны"
}

# Проверка hardcoded путей
check_hardcoded_paths() {
    print_header "Проверка hardcoded путей"

    if grep -r "mnt/c/Users" docker-compose.yml docker-compose.prod.yml ubuntu-*.sh 2>/dev/null; then
        print_error "Найдены hardcoded Windows пути"
        return 1
    else
        print_success "Hardcoded пути не найдены"
    fi
}

# Основная функция
main() {
    local all_good=true

    check_files || all_good=false
    echo ""
    check_extensions || all_good=false
    echo ""
    check_env_vars || all_good=false
    echo ""
    check_production_settings || all_good=false
    echo ""
    check_hardcoded_paths || all_good=false
    echo ""

    if $all_good; then
        print_success "🎉 Проект готов к production развертыванию!"
        echo ""
        echo "🚀 Для развертывания выполните:"
        echo "   ./generate-passwords.sh    # Если пароли слабые"
        echo "   docker-compose -f docker-compose.prod.yml up -d"
    else
        print_error "❌ Проект не готов к production. Исправьте ошибки выше."
        exit 1
    fi
}

main "$@"
