#!/bin/bash

# Скрипт генерации самоподписанных SSL сертификатов для Mayan EDMS
# Использование: ./generate-ssl.sh [domain]

set -e

DOMAIN=${1:-localhost}
CERT_DIR="./certificates"
DAYS=365

echo "🔐 Генерация SSL сертификатов для домена: $DOMAIN"

# Создаем директорию для сертификатов
mkdir -p "$CERT_DIR"

# Генерируем приватный ключ
echo "Создание приватного ключа..."
openssl genrsa -out "$CERT_DIR/ssl.key" 2048

# Генерируем CSR (Certificate Signing Request)
echo "Создание запроса на сертификат..."
cat > "$CERT_DIR/ssl.cnf" << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = RU
ST = Moscow
L = Moscow
O = Mayan EDMS
OU = IT Department
CN = $DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

# Генерируем самоподписанный сертификат
echo "Создание самоподписанного сертификата (срок действия: $DAYS дней)..."
openssl req -new -x509 -key "$CERT_DIR/ssl.key" -out "$CERT_DIR/ssl.crt" -days $DAYS -config "$CERT_DIR/ssl.cnf" -extensions v3_req

# Устанавливаем правильные права доступа
chmod 600 "$CERT_DIR/ssl.key"
chmod 644 "$CERT_DIR/ssl.crt"

echo ""
echo "✅ SSL сертификаты созданы!"
echo "📁 Расположение: $CERT_DIR/"
echo "🔑 Приватный ключ: $CERT_DIR/ssl.key"
echo "📜 Сертификат: $CERT_DIR/ssl.crt"
echo ""
echo "🔧 Для активации HTTPS:"
echo "1. Раскомментируйте строки в docker-compose.simple.yml:"
echo "   MAYAN_COMMON_SSL_CERTIFICATE: \"/opt/mayan/certificates/ssl.crt\""
echo "   MAYAN_COMMON_SSL_KEY: \"/opt/mayan/certificates/ssl.key\""
echo "   - ./certificates:/opt/mayan/certificates:ro"
echo ""
echo "2. Перезапустите Mayan EDMS:"
echo "   docker-compose -f docker-compose.simple.yml down"
echo "   docker-compose -f docker-compose.simple.yml --profile app up -d app"
echo ""
echo "⚠️  ВАЖНО: Это самоподписанный сертификат!"
echo "   Браузер будет показывать предупреждение безопасности."
echo "   Для production используйте сертификаты от Let's Encrypt или другого CA."
