# Инструкция по пересборке и тестированию кеширования

## Пересборка Docker контейнеров

После внесения изменений в код кеширования конфигурации типов документов необходимо пересобрать Docker контейнеры.

### Вариант 1: Пересборка через docker-compose (рекомендуется)

```powershell
# Остановить текущие контейнеры
docker-compose down

# Пересобрать образ приложения (если используется Dockerfile.app)
docker-compose build app

# Запустить контейнеры
docker-compose up -d

# Проверить логи
docker-compose logs -f app
```

### Вариант 2: Пересборка с очисткой кеша

```powershell
# Остановить контейнеры
docker-compose down

# Пересобрать без использования кеша
docker-compose build --no-cache app

# Запустить
docker-compose up -d
```

### Вариант 3: Если используется volume mount (изменения применяются автоматически)

Если в `docker-compose.yml` настроен volume mount для `headless_api`:
```yaml
volumes:
  - ./mayan/apps/headless_api:/opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/headless_api
```

То изменения применяются автоматически без пересборки. Достаточно перезапустить контейнер:

```powershell
docker-compose restart app
```

## Запуск тестов в Docker

### Запуск unit-тестов для кеширования

```powershell
# Войти в контейнер
docker-compose exec app bash

# Запустить тесты
python manage.py test mayan.apps.headless_api.tests.test_config_views_cache --settings=mayan.settings.testing --skip-migrations
```

Или одной командой:

```powershell
docker-compose exec app python manage.py test mayan.apps.headless_api.tests.test_config_views_cache --settings=mayan.settings.testing --skip-migrations
```

### Запуск всех тестов headless_api

```powershell
docker-compose exec app python manage.py test mayan.apps.headless_api.tests --settings=mayan.settings.testing --skip-migrations
```

## Проверка работы кеширования через API

### 1. Проверка списка типов документов

```powershell
# Получить токен аутентификации
$token = "YOUR_TOKEN_HERE"

# Первый запрос (cache MISS)
curl -H "Authorization: Token $token" http://localhost:8080/api/v4/headless/config/document_types/

# Второй запрос (cache HIT - должен быть быстрее)
curl -H "Authorization: Token $token" http://localhost:8080/api/v4/headless/config/document_types/
```

### 2. Проверка детальной конфигурации

```powershell
# Заменить {id} на реальный ID типа документа
curl -H "Authorization: Token $token" http://localhost:8080/api/v4/headless/config/document_types/{id}/
```

### 3. Проверка инвалидации кеша

```powershell
# 1. Сделать запрос (заполнить кеш)
curl -H "Authorization: Token $token" http://localhost:8080/api/v4/headless/config/document_types/{id}/

# 2. Изменить тип документа через админку или API
# (например, изменить label)

# 3. Снова сделать запрос - кеш должен быть инвалидирован
curl -H "Authorization: Token $token" http://localhost:8080/api/v4/headless/config/document_types/{id}/
```

## Проверка логов

```powershell
# Просмотр логов приложения
docker-compose logs -f app | Select-String "cache"

# Просмотр логов с фильтром по кешированию
docker-compose logs app | Select-String -Pattern "cache|Cache|CACHE"
```

## Проверка настроек кеша

```powershell
# Войти в контейнер
docker-compose exec app bash

# Проверить настройки через Django shell
python manage.py shell
```

В Django shell:
```python
from mayan.apps.headless_api import settings as headless_settings

# Проверить TTL
print(f"Cache TTL: {headless_settings.setting_doc_type_config_cache_ttl.value}")

# Проверить версию
print(f"Cache version: {headless_settings.setting_doc_type_config_cache_version.value}")
```

## Очистка кеша вручную

```powershell
# Войти в контейнер
docker-compose exec app bash

# Очистить весь кеш Django
python manage.py shell
```

В Django shell:
```python
from django.core.cache import cache
cache.clear()
```

## Проверка работы сигналов

```powershell
# Войти в контейнер
docker-compose exec app bash

# Запустить Django shell
python manage.py shell
```

В Django shell:
```python
from mayan.apps.documents.models import DocumentType
from django.core.cache import cache
from mayan.apps.headless_api.cache_utils import get_cache_key_list

# Создать тестовый тип документа
doc_type = DocumentType.objects.create(label='Test Cache Type')

# Заполнить кеш (через API или вручную)
cache_key = get_cache_key_list()
cache.set(cache_key, [{'id': doc_type.pk, 'label': doc_type.label}], 3600)

# Проверить, что кеш заполнен
print(f"Cache before: {cache.get(cache_key)}")

# Изменить тип документа (должен триггерить сигнал инвалидации)
doc_type.label = 'Updated Label'
doc_type.save()

# Проверить, что кеш инвалидирован
print(f"Cache after: {cache.get(cache_key)}")
```

## Устранение проблем

### Проблема: Изменения не применяются

**Решение:**
1. Убедитесь, что volume mount настроен правильно в `docker-compose.yml`
2. Перезапустите контейнер: `docker-compose restart app`
3. Если не помогает, пересоберите: `docker-compose build app && docker-compose up -d`

### Проблема: Тесты не запускаются

**Решение:**
1. Убедитесь, что контейнер запущен: `docker-compose ps`
2. Проверьте, что Django установлен: `docker-compose exec app python -c "import django; print(django.VERSION)"`
3. Проверьте настройки: `docker-compose exec app python manage.py check --settings=mayan.settings.testing`

### Проблема: Кеш не работает

**Решение:**
1. Проверьте настройки кеша в `mayan/settings/base.py`
2. Убедитесь, что Redis/локальный кеш доступен
3. Проверьте логи на наличие ошибок: `docker-compose logs app | Select-String "cache"`

