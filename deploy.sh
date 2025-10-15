#!/bin/bash
# Скрипт для автоматического развертывания Mayan EDMS

set -e

print_header() {
    echo -e "\033[0;34m🔧 $1\033[0m"
}

print_success() {
    echo -e "\033[0;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[0;31m❌ $1\033[0m"
}

# Проверка наличия необходимых файлов
check_files() {
    local required_files=("docker-compose.yml" "ubuntu-setup.sh" "ubuntu-prepare.sh" "ubuntu-start.sh")

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Файл $file не найден"
            exit 1
        fi
    done

    print_success "Все необходимые файлы найдены"
}

# Основная функция развертывания
deploy() {
    print_header "🚀 Начинаем автоматическое развертывание Mayan EDMS"

    check_files

    # Проверяем, нужно ли настраивать систему
    if ! docker --version >/dev/null 2>&1 || ! docker-compose --version >/dev/null 2>&1; then
        print_header "Шаг 1: Настройка системы"
        bash ubuntu-setup.sh
    else
        print_success "Система уже настроена, пропускаем установку"
    fi

    print_header "Шаг 2: Подготовка проекта"
    bash ubuntu-prepare.sh

    print_header "Шаг 3: Запуск системы"
    bash ubuntu-start.sh start

    print_header "Шаг 4: Финальная проверка"

    # Ждем полной готовности
    sleep 30

    # Проверяем доступность
    if curl -f -s "http://localhost/" > /dev/null 2>&1; then
        print_success "Mayan EDMS успешно развернут!"
        echo "🌐 Доступен по адресу: http://localhost"
        echo "🔗 Конвертер: http://localhost/#/converter-pipeline/media-conversion/1"
    else
        print_error "Mayan EDMS недоступен"
        exit 1
    fi
}

# Запуск
deploy
