# Mayan EDMS - Команды управления проектом для Ubuntu
#
# Использование:
# make help      - показать справку
# make start     - запустить Mayan EDMS
# make stop      - остановить Mayan EDMS
# make restart   - перезапустить Mayan EDMS
# make logs      - показать логи
# make status    - показать статус
# make clean     - очистить все данные (ВНИМАНИЕ!)

.PHONY: help start stop restart logs status clean setup

help:
	@echo "Mayan EDMS - Управление проектом для Ubuntu"
	@echo ""
	@echo "Команды:"
	@echo "  make setup     - установка зависимостей"
	@echo "  make start     - запустить Mayan EDMS"
	@echo "  make stop      - остановить Mayan EDMS"
	@echo "  make restart   - перезапустить Mayan EDMS"
	@echo "  make logs      - показать логи"
	@echo "  make status    - показать статус"
	@echo "  make clean     - очистить данные (ОПАСНО!)"
	@echo ""

setup:
	@echo "Настройка зависимостей..."
	chmod +x ubuntu-setup.sh
	./ubuntu-setup.sh

start:
	@echo "Запуск Mayan EDMS..."
	chmod +x ubuntu-start.sh
	./ubuntu-start.sh start

stop:
	@echo "Остановка Mayan EDMS..."
	chmod +x ubuntu-start.sh
	./ubuntu-start.sh stop

restart:
	@echo "Перезапуск Mayan EDMS..."
	chmod +x ubuntu-start.sh
	./ubuntu-start.sh restart

logs:
	@echo "Показ логов..."
	chmod +x ubuntu-start.sh
	./ubuntu-start.sh logs

status:
	@echo "Показ статуса..."
	chmod +x ubuntu-start.sh
	./ubuntu-start.sh status

clean:
	@echo "ВНИМАНИЕ: Это удалит ВСЕ данные Mayan EDMS!"
	@echo -n "Продолжить? (y/N): "
	@read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Остановка и очистка..."; \
		chmod +x ubuntu-start.sh; \
		./ubuntu-start.sh stop; \
		echo "Удаление данных..."; \
		sudo rm -rf docker/mayan_data/* docker/postgres_data/* docker/rabbitmq_data/* docker/redis_data/* 2>/dev/null || true; \
		echo "Очистка завершена"; \
	else \
		echo "Операция отменена"; \
	fi