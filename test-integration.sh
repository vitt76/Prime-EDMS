#!/bin/bash

echo "🧪 Testing Prime-EDMS Integration"
echo "=================================="

BASE_URL="http://localhost:8080"

# Тест 1: Проверка доступности API
echo "1. Testing API availability..."
if curl -f "$BASE_URL/api/v4/" > /dev/null 2>&1; then
  echo "✅ API is accessible"
else
  echo "❌ API is not accessible"
  exit 1
fi

# Тест 2: Получение учетных данных autoadmin
echo "2. Testing auto admin credentials endpoint..."
CREDENTIALS=$(curl -s "$BASE_URL/autoadmin-api/credentials/")
if echo "$CREDENTIALS" | grep -q '"is_auto_generated"'; then
  echo "✅ Auto admin credentials endpoint works"

  # Проверяем, что учетные данные получены
  if echo "$CREDENTIALS" | grep -q '"is_auto_generated":true'; then
    USERNAME=$(echo "$CREDENTIALS" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    PASSWORD=$(echo "$CREDENTIALS" | grep -o '"password":"[^"]*"' | cut -d'"' -f4)
    echo "   📝 Credentials found: $USERNAME / $PASSWORD"
  else
    echo "   ⚠️ No auto-generated credentials available"
  fi
else
  echo "❌ Auto admin credentials endpoint failed"
  exit 1
fi

# Тест 3: Проверка фронтенда
echo "3. Testing frontend availability..."
if curl -f http://localhost:5173 > /dev/null 2>&1; then
  echo "✅ Frontend is accessible"
else
  echo "❌ Frontend is not accessible"
  exit 1
fi

# Тест 4: Проверка token аутентификации (опционально)
echo "4. Testing token authentication..."
if echo "$CREDENTIALS" | grep -q '"is_auto_generated":true'; then
  TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v4/auth/token/obtain/" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

  if echo "$TOKEN_RESPONSE" | grep -q '"token"'; then
    echo "✅ Token authentication works"
  else
    echo "⚠️ Token authentication may need manual testing"
  fi
else
  echo "⚠️ Skipping token authentication test - no credentials"
fi

echo ""
echo "🎉 Integration tests completed!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:80"
echo ""
echo "📋 Next steps:"
echo "1. Open frontend in browser"
echo "2. Check if login form is auto-filled"
echo "3. Try to login with provided credentials"
