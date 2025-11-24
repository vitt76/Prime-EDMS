# 🚀 Комплексный план оптимизации производительности поиска

## 📊 Текущее состояние

### Уже реализованные оптимизации:
1. ✅ Индекс на `filename` (DocumentFile)
2. ✅ Индекс на `label` (Document)
3. ✅ Оптимизация `cleanup_query` - только 4 приоритетных поля для простого поиска
4. ✅ Оптимизация `SearchQuery` - ограничение полей
5. ✅ `select_related('document_type')` для избежания N+1 запросов

### Обнаруженные проблемы:
- ❌ Нет индекса на `description` (TextField)
- ❌ Нет debouncing на фронтенде - каждый символ вызывает запрос
- ❌ Нет кеширования результатов поиска
- ❌ `distinct()` может быть медленным на больших таблицах
- ❌ Нет оптимизации для поиска по JSON полям (ai_tags, categories)
- ❌ Нет полнотекстового поиска PostgreSQL (pg_trgm)

---

## 🎯 Приоритетные оптимизации (по эффективности)

### 1. 🔥 КРИТИЧНО: Debouncing на фронтенде (улучшение UX в 10+ раз)

**Проблема:** Каждый символ в поле поиска вызывает запрос к серверу, что создает огромную нагрузку.

**Решение:** Добавить debouncing с задержкой 300-500ms.

**Файл:** `mayan/apps/dynamic_search/templates/dynamic_search/app/list_toolbar.html`

```javascript
// Добавить после строки 44
let searchTimeout;
const SEARCH_DEBOUNCE_MS = 400; // Задержка перед отправкой запроса

$filterInputTerms.on('input', function () {
    const $this = $(this);
    const searchValue = $this.val().trim();
    
    // Очищаем предыдущий таймер
    clearTimeout(searchTimeout);
    
    // Показываем индикатор загрузки
    $this.addClass('search-loading');
    
    // Если поле пустое, сразу очищаем результаты
    if (!searchValue) {
        $formFilter.submit();
        return;
    }
    
    // Устанавливаем новый таймер
    searchTimeout = setTimeout(function() {
        $this.removeClass('search-loading');
        $formFilter.submit();
    }, SEARCH_DEBOUNCE_MS);
});
```

**Ожидаемый эффект:** Снижение количества запросов в 5-10 раз, улучшение UX.

---

### 2. 🔥 КРИТИЧНО: Кеширование результатов поиска

**Проблема:** Повторные запросы с одинаковыми параметрами выполняются заново.

**Решение:** Кешировать результаты в Redis на 5-10 минут.

**Файл:** `mayan/apps/dynamic_search/backends/django.py`

```python
from django.core.cache import cache
import hashlib
import json

class DjangoSearchBackend(SearchBackend):
    def _search(
        self, query, search_model, user, global_and_search=False,
        ignore_limit=False
    ):
        # Создаем ключ кеша
        cache_key = self._get_cache_key(query, search_model, user, global_and_search)
        
        # Пытаемся получить из кеша
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug('Search cache HIT: %s', cache_key[:50])
            # Возвращаем queryset с закешированными ID
            return search_model.get_queryset().filter(pk__in=cached_result)
        
        logger.debug('Search cache MISS: %s', cache_key[:50])
        
        # Выполняем поиск
        search_query = self.get_search_query(
            global_and_search=global_and_search, query=query,
            search_model=search_model
        )
        
        base_queryset = search_model.get_queryset()
        
        if hasattr(base_queryset.model, 'document_type'):
            base_queryset = base_queryset.select_related('document_type')
        
        if search_query.django_query:
            queryset = base_queryset.filter(
                search_query.django_query
            ).distinct()
        else:
            queryset = base_queryset.none()
        
        # Кешируем только ID (не объекты) для экономии памяти
        result_ids = list(queryset.values_list('pk', flat=True)[:1000])  # Ограничиваем до 1000
        
        # Кешируем на 5 минут
        cache.set(cache_key, result_ids, 300)
        
        return queryset
    
    def _get_cache_key(self, query, search_model, user, global_and_search):
        """Генерирует уникальный ключ кеша для запроса."""
        # Сортируем query для консистентности
        query_str = json.dumps(sorted(query.items()), sort_keys=True)
        key_data = f"{search_model.get_full_name()}:{user.pk}:{global_and_search}:{query_str}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"search:{key_hash}"
```

**Ожидаемый эффект:** Ускорение повторных запросов в 10-100 раз.

---

### 3. ⚡ ВЫСОКИЙ ПРИОРИТЕТ: Оптимизация distinct() запросов

**Проблема:** `distinct()` на больших таблицах с JOIN может быть очень медленным.

**Решение:** Использовать `values_list('id')` для получения ID, затем загружать объекты.

**Файл:** `mayan/apps/dynamic_search/backends/django.py`

```python
def _search(self, query, search_model, user, global_and_search=False, ignore_limit=False):
    # ... существующий код ...
    
    if search_query.django_query:
        # Оптимизация: сначала получаем только ID через values_list
        # Это быстрее, чем distinct() на полных объектах
        result_ids = base_queryset.filter(
            search_query.django_query
        ).values_list('id', flat=True).distinct()
        
        # Затем загружаем объекты по ID
        queryset = search_model.get_queryset().filter(pk__in=result_ids)
    else:
        queryset = base_queryset.none()
    
    return queryset
```

**Ожидаемый эффект:** Ускорение на 20-50% для запросов с JOIN.

---

### 4. ⚡ ВЫСОКИЙ ПРИОРИТЕТ: Индекс на description (GIN для полнотекстового поиска)

**Проблема:** `description` - это TextField без индекса, поиск по нему медленный.

**Решение:** Создать GIN индекс с использованием pg_trgm для PostgreSQL.

**Файл:** `mayan/apps/documents/migrations/0082_document_description_gin_index.py`

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.operations import BtreeGinExtension
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0081_documentfile_filename_index'),
    ]

    operations = [
        BtreeGinExtension(),
        migrations.RunSQL(
            # Создаем GIN индекс с триграммами для быстрого поиска
            sql="CREATE INDEX IF NOT EXISTS documents_document_description_gin_idx "
                "ON documents_document USING gin (description gin_trgm_ops);",
            reverse_sql="DROP INDEX IF EXISTS documents_document_description_gin_idx;"
        ),
    ]
```

**Ожидаемый эффект:** Ускорение поиска по description в 5-10 раз.

---

### 5. 📈 СРЕДНИЙ ПРИОРИТЕТ: Оптимизация поиска по JSON полям

**Проблема:** Поиск по JSON полям (ai_tags, categories) использует transformation функции, что медленно.

**Решение:** Использовать нативные JSON lookup'ы PostgreSQL.

**Файл:** `mayan/apps/dam/search.py`

```python
# В FieldQuery.__init__ для JSON полей использовать нативные lookup'ы
if search_field.field.startswith('ai_analysis__'):
    # Для JSON полей используем нативные PostgreSQL lookup'ы
    if 'ai_tags' in search_field.field or 'categories' in search_field.field:
        # Используем JSONB contains для поиска в массивах
        q_object = Q(
            **{f'{field_path}__contains': [term_string]}
        )
    else:
        # Для текстовых JSON полей используем icontains
        q_object = Q(
            **{f'{field_path}__icontains': term_string}
        )
```

**Ожидаемый эффект:** Ускорение поиска по AI метаданным в 3-5 раз.

---

### 6. 📈 СРЕДНИЙ ПРИОРИТЕТ: Составные индексы для частых комбинаций

**Проблема:** Поиск по нескольким полям одновременно может быть медленным.

**Решение:** Создать составные индексы для частых комбинаций.

**Файл:** `mayan/apps/documents/migrations/0083_document_composite_indexes.py`

```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0082_document_description_gin_index'),
    ]

    operations = [
        migrations.RunSQL(
            # Составной индекс для частых комбинаций: label + in_trash
            sql="CREATE INDEX IF NOT EXISTS documents_document_label_trash_idx "
                "ON documents_document (label, in_trash) WHERE in_trash = false;",
            reverse_sql="DROP INDEX IF EXISTS documents_document_label_trash_idx;"
        ),
    ]
```

**Ожидаемый эффект:** Ускорение комбинированных запросов на 10-20%.

---

### 7. 📊 НИЗКИЙ ПРИОРИТЕТ: Оптимизация AccessControlList проверок

**Проблема:** Проверка прав доступа для каждого документа может быть медленной.

**Решение:** Кешировать права доступа пользователя и использовать prefetch_related.

**Файл:** `mayan/apps/dynamic_search/classes.py` (метод `search`)

```python
def search(self, query, search_model, user, global_and_search=False):
    # ... существующий код ...
    
    if search_model.permission:
        # Кешируем права доступа пользователя
        cache_key = f"user_permissions:{user.pk}:{search_model.permission}"
        cached_permissions = cache.get(cache_key)
        
        if cached_permissions is None:
            queryset = AccessControlList.objects.restrict_queryset(
                permission=search_model.permission, queryset=queryset,
                user=user
            )
            # Кешируем на 1 час
            cache.set(cache_key, list(queryset.values_list('pk', flat=True)), 3600)
        else:
            queryset = queryset.filter(pk__in=cached_permissions)
    
    return SearchBackend.limit_queryset(queryset=queryset)
```

**Ожидаемый эффект:** Ускорение на 5-10% для пользователей с большим количеством документов.

---

## 🧪 План глубокого тестирования

### 1. Бенчмарки производительности

**Скрипт:** `mayan/apps/documents/management/commands/benchmark_search.py`

```python
import time
from django.core.management.base import BaseCommand
from mayan.apps.dynamic_search.classes import SearchBackend
from mayan.apps.documents.models import Document

class Command(BaseCommand):
    help = 'Benchmark search performance'

    def add_arguments(self, parser):
        parser.add_argument('--iterations', type=int, default=10, help='Number of iterations')
        parser.add_argument('--query', type=str, default='test', help='Search query')

    def handle(self, *args, **options):
        iterations = options['iterations']
        query = options['query']
        backend = SearchBackend.get_instance()
        
        # Тест 1: Простой поиск
        times = []
        for i in range(iterations):
            start = time.time()
            results = backend.search(
                query={'q': query},
                search_model=Document.search_model,
                user=None
            )
            elapsed = time.time() - start
            times.append(elapsed)
            self.stdout.write(f"Iteration {i+1}: {elapsed:.3f}s, results: {results.count()}")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        self.stdout.write(self.style.SUCCESS(
            f"\nSimple search benchmark:\n"
            f"  Average: {avg_time:.3f}s\n"
            f"  Min: {min_time:.3f}s\n"
            f"  Max: {max_time:.3f}s\n"
        ))
        
        # Тест 2: Поиск по filename
        # ... аналогично
```

### 2. Профилирование SQL запросов

**Команда:**
```bash
docker-compose exec app python manage.py benchmark_search --query "test" --iterations 10
```

**Анализ:**
- Использовать Django Debug Toolbar для анализа SQL запросов
- Проверить EXPLAIN для каждого запроса
- Найти медленные запросы (N+1 проблемы)

### 3. Нагрузочное тестирование

**Скрипт:** `load_test_search.py`

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def search_request(query):
    start = time.time()
    response = requests.get(
        'http://localhost:8080/api/v4/search/documents.Document/',
        params={'q': query},
        auth=('admin', 'admin')
    )
    elapsed = time.time() - start
    return elapsed, response.status_code

# Тест с 50 параллельными запросами
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(search_request, 'test') for _ in range(50)]
    results = [f.result() for f in futures]

avg_time = sum(r[0] for r in results) / len(results)
print(f"Average response time: {avg_time:.3f}s")
```

---

## 📊 Метрики для мониторинга

### Ключевые метрики:
1. **Время ответа поиска** (p50, p95, p99)
2. **Количество SQL запросов** на один поисковый запрос
3. **Cache hit rate** для кеширования поиска
4. **Количество обрабатываемых полей** в cleanup_query
5. **Использование памяти** при поиске

### Настройка мониторинга:

**Файл:** `mayan/apps/dynamic_search/middleware.py` (новый)

```python
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SearchPerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'q=' in request.GET.urlencode() or '/search/' in request.path:
            request._search_start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, '_search_start_time'):
            elapsed = time.time() - request._search_start_time
            logger.info(
                f"Search performance: {elapsed:.3f}s, "
                f"query={request.GET.get('q', '')[:50]}, "
                f"path={request.path}"
            )
        return response
```

---

## 🎯 Целевые показатели производительности

### После всех оптимизаций:

| Тип поиска | Текущее время | Целевое время | Улучшение |
|------------|---------------|---------------|-----------|
| Простой поиск (q=test) | ~5s | <0.5s | 10x |
| Поиск по filename | ~3s | <0.3s | 10x |
| Поиск по description | ~4s | <0.4s | 10x |
| Расширенный поиск | ~6s | <1s | 6x |
| Повторный запрос (cache) | ~5s | <0.05s | 100x |

---

## 📝 План внедрения (по приоритетам)

### Фаза 1 (Критично - немедленно):
1. ✅ Debouncing на фронтенде
2. ✅ Кеширование результатов поиска

### Фаза 2 (Высокий приоритет - в течение недели):
3. ✅ Оптимизация distinct()
4. ✅ GIN индекс на description

### Фаза 3 (Средний приоритет - в течение месяца):
5. ✅ Оптимизация JSON полей
6. ✅ Составные индексы

### Фаза 4 (Низкий приоритет - по необходимости):
7. ✅ Оптимизация ACL проверок

---

## 🔧 Инструменты для тестирования

1. **Django Debug Toolbar** - анализ SQL запросов
2. **django-extensions** - команда `runprofileserver` для профилирования
3. **pg_stat_statements** - анализ медленных SQL запросов в PostgreSQL
4. **Redis MONITOR** - мониторинг кеш-запросов

---

## 📚 Дополнительные ресурсы

- [Django QuerySet Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [PostgreSQL pg_trgm Extension](https://www.postgresql.org/docs/current/pgtrgm.html)

