#!/bin/bash

echo "🚀 Starting Prime-EDMS Integrated System"
echo "========================================"

# Запуск Docker containers
echo "📦 Starting Docker services..."
docker-compose up -d

# Ожидание готовности бэкенда
echo "⏳ Waiting for backend to be ready..."
until curl -f http://localhost:8080/api/v4/ > /dev/null 2>&1; do
  echo "Backend not ready, waiting..."
  sleep 5
done

echo "✅ Backend is ready!"

# Получение учетных данных autoadmin
echo "🔑 Fetching auto-generated credentials..."
CREDENTIALS=$(curl -s http://localhost:8080/autoadmin-api/credentials/)
if echo "$CREDENTIALS" | grep -q '"is_auto_generated":true'; then
  USERNAME=$(echo "$CREDENTIALS" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  PASSWORD=$(echo "$CREDENTIALS" | grep -o '"password":"[^"]*"' | cut -d'"' -f4)
  echo "📝 Auto-generated credentials:"
  echo "   Username: $USERNAME"
  echo "   Password: $PASSWORD"
  echo ""
fi

# Запуск фронтенда
echo "🎨 Starting frontend..."
cd frontend
npm run dev
