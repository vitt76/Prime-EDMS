#!/bin/bash

# Быстрый тест Mayan EDMS для Ubuntu
# Использование: ./test-mayan.sh

echo "🧪 Тестирование Mayan EDMS..."

cd ~/Prime-EDMS

# Проверяем статус контейнеров
echo "📊 Статус контейнеров:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Проверяем логи приложения
echo ""
echo "📋 Последние логи приложения:"
docker logs prime-edms_app_1 | tail -10

# Тестируем подключение
echo ""
echo "🌐 Тест подключения:"
if curl -s --max-time 5 http://localhost > /dev/null; then
    echo "✅ Mayan EDMS доступен на http://localhost"
else
    echo "❌ Mayan EDMS недоступен"
fi

# Проверяем сервисы
echo ""
echo "🔍 Проверка сервисов:"
echo -n "PostgreSQL: "
if docker exec prime-edms_postgresql_1 pg_isready -U mayan >/dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "Redis: "
if docker exec prime-edms_redis_1 redis-cli ping >/dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "RabbitMQ: "
if docker exec prime-edms_rabbitmq_1 rabbitmqctl node_health_check >/dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo ""
echo "💡 Если есть проблемы, попробуйте:"
echo "  ./ubuntu-start.sh clean    # Очистить данные"
echo "  ./ubuntu-start.sh start    # Перезапустить"
echo "  ./ubuntu-start.sh logs     # Посмотреть логи"
