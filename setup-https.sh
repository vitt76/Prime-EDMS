#!/bin/bash

# Скрипт настройки HTTPS для Mayan EDMS
# Поддерживает самоподписанные сертификаты и Let's Encrypt

set -e

echo "🔒 Настройка HTTPS для Mayan EDMS"
echo ""

# Проверяем аргументы
if [ $# -eq 0 ]; then
    echo "Использование:"
    echo "  $0 self-signed [domain]  - Создать самоподписанный сертификат"
    echo "  $0 letsencrypt <domain>  - Настроить Let's Encrypt (требуется домен)"
    echo ""
    echo "Примеры:"
    echo "  $0 self-signed localhost"
    echo "  $0 letsencrypt mymayan.com"
    exit 1
fi

TYPE=$1
DOMAIN=${2:-localhost}

case $TYPE in
    "self-signed")
        echo "🔐 Создание самоподписанного SSL сертификата..."
        ./generate-ssl.sh "$DOMAIN"

        echo ""
        echo "📝 Активация HTTPS в docker-compose.simple.yml:"
        echo "Раскомментируйте следующие строки:"
        echo ""
        echo "  MAYAN_COMMON_SSL_CERTIFICATE: \"/opt/mayan/certificates/ssl.crt\""
        echo "  MAYAN_COMMON_SSL_KEY: \"/opt/mayan/certificates/ssl.key\""
        echo "  - ./certificates:/opt/mayan/certificates:ro"
        echo ""
        echo "⚠️  Браузер будет показывать предупреждение о самоподписанном сертификате"
        ;;

    "letsencrypt")
        if [ "$DOMAIN" = "localhost" ]; then
            echo "❌ Let's Encrypt не работает с localhost. Используйте реальный домен."
            exit 1
        fi

        echo "🔐 Настройка Let's Encrypt для домена: $DOMAIN"
        echo ""
        echo "📋 Требования:"
        echo "1. Домен $DOMAIN должен указывать на этот сервер"
        echo "2. Порты 80 и 443 должны быть открыты"
        echo ""
        echo "🔧 Установка Certbot..."

        # Определяем дистрибутив
        if command -v apt >/dev/null 2>&1; then
            # Ubuntu/Debian
            sudo apt update
            sudo apt install -y certbot
        elif command -v yum >/dev/null 2>&1; then
            # CentOS/RHEL
            sudo yum install -y certbot
        else
            echo "❌ Неизвестный дистрибутив. Установите Certbot вручную."
            exit 1
        fi

        echo ""
        echo "📜 Получение SSL сертификата..."
        sudo certbot certonly --standalone -d "$DOMAIN"

        CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
        if [ ! -d "$CERT_PATH" ]; then
            echo "❌ Сертификат не был создан"
            exit 1
        fi

        echo ""
        echo "✅ SSL сертификат получен!"
        echo ""
        echo "📝 Активация HTTPS в docker-compose.simple.yml:"
        echo "Замените переменные окружения:"
        echo ""
        echo "  MAYAN_COMMON_SSL_CERTIFICATE: \"$CERT_PATH/fullchain.pem\""
        echo "  MAYAN_COMMON_SSL_KEY: \"$CERT_PATH/privkey.pem\""
        echo "  - $CERT_PATH:/etc/letsencrypt/live/$DOMAIN:ro"
        echo ""
        echo "🔄 Настройка автоматического обновления сертификатов:"
        echo "sudo crontab -e"
        echo "Добавьте строку:"
        echo "0 12 * * * /usr/bin/certbot renew --quiet"
        ;;

    *)
        echo "❌ Неизвестный тип: $TYPE"
        echo "Используйте: self-signed или letsencrypt"
        exit 1
        ;;
esac

echo ""
echo "🚀 После настройки перезапустите Mayan EDMS:"
echo "docker-compose -f docker-compose.simple.yml --profile app down"
echo "docker-compose -f docker-compose.simple.yml --profile app up -d app"
echo ""
echo "🌐 Mayan EDMS будет доступен по HTTPS: https://$DOMAIN"
