# Mayan EDMS - Команды управления проектом
#
# Использование в WSL2/Linux:
# make help          - показать справку
# make start         - запустить Mayan EDMS
# make stop          - остановить Mayan EDMS
# make restart       - перезапустить Mayan EDMS
# make logs          - показать логи
# make status        - показать статус
# make clean         - очистить все данные (ВНИМАНИЕ!)
#
# Использование в Windows PowerShell:
# .\start-mayan.ps1   - запустить
# .\start-mayan.ps1 -Stop   - остановить
# .\start-mayan.ps1 -Logs   - логи
# .\start-mayan.ps1 -Status - статус

# Загружаем переменные окружения если файл существует
ifneq (,$(wildcard .env))
include .env
export
endif

COMPOSE_FILE ?= docker-compose.yml
PROJECT_NAME ?= prime-edms

.PHONY: help start stop restart logs logs-app status clean setup prepare ubuntu-setup ubuntu-start ubuntu-prepare

help:
	@echo "Mayan EDMS - Управление проектом"
	@echo ""
	@echo "Команды:"
	@echo "  make setup     - настройка WSL2 и Docker"
	@echo "  make start     - запустить Mayan EDMS"
	@echo "  make stop      - остановить Mayan EDMS"
	@echo "  make restart   - перезапустить Mayan EDMS"
	@echo "  make logs      - логи всех сервисов"
	@echo "  make logs-app  - логи только приложения"
	@echo "  make status    - статус контейнеров"
	@echo "  make clean     - очистить данные (ОПАСНО!)"
	@echo ""
	@echo "Установка на Ubuntu:"
	@echo "  make ubuntu-setup  - настройка Ubuntu и Docker"
	@echo "  make ubuntu-prepare - подготовка проекта Mayan EDMS"
	@echo "  make ubuntu-start   - управление Mayan EDMS на Ubuntu"
	@echo ""
	@echo "Или используйте PowerShell скрипт: .\start-mayan.ps1"

setup:
	@echo "Настройка WSL2 и Docker..."
	chmod +x setup-wsl.sh
	./setup-wsl.sh

start:
	@echo "Запуск Mayan EDMS..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Ожидание запуска..."
	sleep 10
	docker-compose -f $(COMPOSE_FILE) ps

stop:
	@echo "Остановка Mayan EDMS..."
	docker-compose -f $(COMPOSE_FILE) down

restart:
	@echo "Перезапуск Mayan EDMS..."
	docker-compose -f $(COMPOSE_FILE) restart
	sleep 5
	docker-compose -f $(COMPOSE_FILE) ps

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-app:
	docker logs -f prime-edms_app_1

status:
	@echo "=== Статус контейнеров ==="
	docker-compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "=== Использование ресурсов ==="
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

clean:
	@echo "ВНИМАНИЕ: Это удалит ВСЕ данные Mayan EDMS!"
	@echo -n "Продолжить? (y/N): "
	@read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Остановка и очистка..."; \
		docker-compose -f $(COMPOSE_FILE) down -v; \
		docker volume rm $(PROJECT_NAME)_app_data $(PROJECT_NAME)_postgres_data $(PROJECT_NAME)_redis_data $(PROJECT_NAME)_rabbitmq_data 2>/dev/null || true; \
		echo "Очистка завершена"; \
	else \
		echo "Операция отменена"; \
	fi

# Команды для Ubuntu
ubuntu-setup:
	@echo "🐳 Настройка Ubuntu для Mayan EDMS..."
	./ubuntu-setup.sh

ubuntu-prepare:
	@echo "🔧 Подготовка проекта Mayan EDMS..."
	./ubuntu-prepare.sh

ubuntu-start:
	@echo "🚀 Управление Mayan EDMS на Ubuntu..."
	./ubuntu-start.sh