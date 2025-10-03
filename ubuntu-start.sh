#!/bin/bash

# Скрипт управления Mayan EDMS для Ubuntu
# Использование: ./ubuntu-start.sh [start|stop|restart|logs|status|clean]

set -e

COMPOSE_FILE="docker-compose.simple.yml"
PROJECT_NAME="mayan-edms"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции
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

# Проверка Docker
check_docker() {
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
}

# Запуск Mayan EDMS
start_mayan() {
    print_header "Запуск Mayan EDMS..."

    # Проверка существования контейнеров
    if docker ps -q -f name="$PROJECT_NAME" | grep -q .; then
        print_warning "Mayan EDMS уже запущен"
        return 0
    fi

    # Запускаем только инфраструктуру (БД, Redis, RabbitMQ)
    docker-compose -f $COMPOSE_FILE up -d postgresql redis rabbitmq
    print_success "Ожидание готовности сервисов..."

    # Ждем готовности PostgreSQL
    print_header "Ожидание PostgreSQL..."
    for i in {1..30}; do
        if docker exec $PROJECT_NAME-postgresql-1 pg_isready -U mayan >/dev/null 2>&1; then
            print_success "PostgreSQL готов"
            break
        fi
        sleep 5
        echo -n "."
    done

    # Ждем готовности Redis
    print_header "Ожидание Redis..."
    for i in {1..20}; do
        if docker exec $PROJECT_NAME-redis-1 redis-cli ping >/dev/null 2>&1; then
            print_success "Redis готов"
            break
        fi
        sleep 3
        echo -n "."
    done

    # Ждем готовности RabbitMQ
    print_header "Ожидание RabbitMQ..."
    for i in {1..40}; do
        if docker exec $PROJECT_NAME-rabbitmq-1 rabbitmqctl node_health_check >/dev/null 2>&1; then
            print_success "RabbitMQ готов"
            break
        fi
        sleep 5
        echo -n "."
    done

    print_success "Все сервисы готовы! Запуск Mayan EDMS..."
    sleep 10

    # Запускаем само приложение
    docker-compose -f $COMPOSE_FILE --profile app up -d app
    sleep 30

    # Проверка статуса
    if docker-compose -f $COMPOSE_FILE ps | grep -q "prime-edms_app.*Up"; then
        print_success "Mayan EDMS запущен!"
        echo ""
        echo -e "${BLUE}🌐 Доступен по адресу: http://localhost${NC}"
    else
        print_error "Ошибка запуска приложения. Проверьте логи: ./ubuntu-start.sh logs"
        exit 1
    fi
}

# Остановка Mayan EDMS
stop_mayan() {
    print_header "Остановка Mayan EDMS..."
    docker-compose -f $COMPOSE_FILE --profile app down
    print_success "Mayan EDMS остановлен"
}

# Перезапуск Mayan EDMS
restart_mayan() {
    print_header "Перезапуск Mayan EDMS..."
    docker-compose -f $COMPOSE_FILE --profile app restart
    sleep 30

    if docker-compose -f $COMPOSE_FILE ps | grep -q "prime-edms_app.*Up"; then
        print_success "Mayan EDMS перезапущен"
    else
        print_error "Ошибка перезапуска"
    fi
}

# Просмотр логов
show_logs() {
    print_header "Логи Mayan EDMS (Ctrl+C для выхода):"
    docker-compose -f $COMPOSE_FILE --profile app logs -f
}

# Статус системы
show_status() {
    print_header "Статус контейнеров:"
    docker-compose -f $COMPOSE_FILE --profile app ps

    echo ""
    print_header "Healthchecks:"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$PROJECT_NAME\|NAMES" || echo "Нет запущенных контейнеров"

    echo ""
    print_header "Использование ресурсов:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || \
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Очистка системы
clean_system() {
    print_warning "Это действие удалит ВСЕ данные Mayan EDMS!"
    read -p "Продолжить? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_header "Остановка и очистка..."

        # Остановка контейнеров
        docker-compose -f $COMPOSE_FILE --profile app down -v 2>/dev/null || true

        # Удаление volumes
        docker volume rm ${PROJECT_NAME}_postgres_data ${PROJECT_NAME}_redis_data ${PROJECT_NAME}_rabbitmq_data ${PROJECT_NAME}_app_data 2>/dev/null || true

        # Очистка неиспользуемых ресурсов
        docker system prune -f >/dev/null 2>&1

        print_success "Очистка завершена"
    else
        print_warning "Операция отменена"
    fi
}

# Справка
show_help() {
    echo "Управление Mayan EDMS для Ubuntu"
    echo ""
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "Команды:"
    echo "  start   - Запустить Mayan EDMS"
    echo "  stop    - Остановить Mayan EDMS"
    echo "  restart - Перезапустить Mayan EDMS"
    echo "  logs    - Показать логи"
    echo "  status  - Показать статус"
    echo "  clean   - Очистить все данные (ОПАСНО!)"
    echo "  help    - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 start    # Запуск"
    echo "  $0 logs     # Логи"
    echo "  $0 status   # Статус"
}

# Основная логика
main() {
    local command="$1"

    case "$command" in
        start)
            check_docker
            start_mayan
            ;;
        stop)
            stop_mayan
            ;;
        restart)
            check_docker
            restart_mayan
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        clean)
            clean_system
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            if [ -z "$command" ]; then
                check_docker
                start_mayan
            else
                print_error "Неизвестная команда: $command"
                echo ""
                show_help
                exit 1
            fi
            ;;
    esac
}

main "$@"
