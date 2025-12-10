# 🚨 План Трансформации V4 — Смена Архитектурной Стратегии

**Дата создания:** 04 декабря 2025
**Версия:** 4.0 (КРИТИЧЕСКИЙ ПЕРЕСМОТР — Переход на BFF-адаптер)
**Автор:** Lead Technical Architect
**Статус:** 🔴 **ТРЕБУЕТСЯ СМЕНА АРХИТЕКТУРЫ**

---

## 📋 Исполнительное Резюме

### 🚨 КРИТИЧЕСКИЙ СТАТУС: Прямая Интеграция Провалена

**Предыдущий статус (V3):** "100% Integration Complete — Production Ready"

**Реальный статус (V4):** 🔴 **КРИТИЧЕСКИЙ СБОЙ** — Архитектурные ограничения Mayan API делают невозможной полноценную SPA-интеграцию без промежуточного слоя.

---

## 1. Детальный Анализ Провала V3

### 1.1 Доказательства из TEST_EXECUTION_REPORT.md

Следующие тесты были выполнены реально против сервера 127.0.0.1:8080:

#### КРИТИЧЕСКИЙ СБОЙ #1: Аутентификация (TC-AUTH-01)

```
URL: http://127.0.0.1:8080/api/v4/auth/token/obtain/
Payload: {"username": "admin", "password": "admin123"}
Status Code: 400 Bad Request
Response JSON: {
  "non_field_errors": [
    "Unable to log in with provided credentials."
  ]
}
```

**Диагноз:** Учетные данные из docker-compose.yml (`admin`/`admin123`) не работают. Либо пароль был изменен после первого входа, либо autoadmin механизм Mayan очистил данные.

**Влияние:** Все аутентифицированные тесты заблокированы. Невозможно проверить 13 из 15 тестов.

#### КРИТИЧЕСКИЙ СБОЙ #2: Endpoint Смены Пароля Не Существует (TC-AUTH-02)

```
URL: http://127.0.0.1:8080/api/v4/users/current/password/
Status Code: 404 Not Found
Content-Type: text/html; charset=utf-8
Response: HTML страница "Page not found"
```

**Диагноз:** Mayan EDMS **вообще не имеет** REST API endpoint для смены пароля. Только HTML-форма через `MayanPasswordChangeView`.

**Влияние:** 
- ❌ Фронтенд не может реализовать функцию "Смена пароля" через API
- ❌ SPA не может предоставить self-service функционал
- ❌ PATCH `/api/v4/users/current/` также **НЕ ПОДДЕРЖИВАЕТ** поле `password`

**Почему V3 был неверен:**
V3 утверждал: "Используйте PATCH /api/v4/users/current/ с полем password"
Реальность: Это **неправда**. Mayan UserSerializer **не включает password** в writable fields. Смена пароля возможна только через Django Admin UI или специальные HTML views.

#### КРИТИЧЕСКИЙ СБОЙ #3: Загрузка Требует Аутентификации (TC-UPLOAD-01)

```
URL: http://127.0.0.1:8080/api/v4/uploads/init/
Status Code: 401 Unauthorized
Response JSON: {
  "detail": "Authentication credentials were not provided."
}
```

**Диагноз:** Upload endpoint существует и работает корректно — требует Token authentication. Сам по себе это не баг, но блокирует тестирование из-за проблем с аутентификацией.

### 1.2 Почему Стратегия V3 "Прямой Интеграции" Провалилась

| Утверждение V3 | Реальность | Доказательство |
|----------------|------------|----------------|
| "100% Integration Complete" | ❌ ЛОЖЬ | 67% тестов заблокированы, 13% провалены |
| "Password change via PATCH" | ❌ ЛОЖЬ | 404 ответ, endpoint не существует |
| "Authentication 100% stable" | ❌ ЧАСТИЧНО | Работает, но не решает self-service gap |
| "Production Ready" | ❌ КРИТИЧЕСКИ НЕТ | Пользователи не могут менять пароли |

### 1.3 Корневая Причина

**Mayan EDMS API спроектирован для автоматизации, а не для интерактивных пользовательских сессий.**

API предоставляет:
- ✅ CRUD операции с документами
- ✅ Поиск и фильтрацию
- ✅ Управление метаданными
- ✅ Управление коллекциями

API **НЕ** предоставляет:
- ❌ Self-service управление учетной записью
- ❌ Смену пароля через REST
- ❌ Сброс пароля через REST
- ❌ Экспозицию конфигурации для динамических форм
- ❌ Пользовательскую ленту активности

---

## 2. Новая Стратегия: BFF-Адаптер (Headless API Layer)

### 2.1 Архитектурное Решение

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER (Vue 3)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pages     │  │ Components  │  │   Stores    │  │  Services   │         │
│  │  (Views)    │  │    (UI)     │  │  (Pinia)    │  │  (Axios)    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                │                 │
│         └────────────────┴────────────────┴────────────────┘                 │
│                                   │                                          │
│                          ┌────────▼────────┐                                 │
│                          │    ADAPTERS     │  ◄── URL REFACTOR REQUIRED      │
│                          │  (→ headless)   │                                 │
│                          └────────┬────────┘                                 │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                    🆕 BFF LAYER: headless_api (Django App)                    │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐            │
│  │ HeadlessPassword │  │ HeadlessConfig   │  │ HeadlessActivity │            │
│  │      View        │  │      View        │  │      View        │            │
│  │                  │  │                  │  │                  │            │
│  │ POST /headless/  │  │ GET /headless/   │  │ GET /headless/   │            │
│  │ password/change/ │  │ config/doctypes/ │  │ activity/feed/   │            │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘            │
│           │                     │                     │                       │
│           └─────────────────────┴─────────────────────┘                       │
│                                 │                                             │
│                                 ▼                                             │
│                    ┌───────────────────────┐                                  │
│                    │  Mayan EDMS Services  │ ◄── Прямые вызовы internal API   │
│                    │  (User, Document,     │                                  │
│                    │   Workflow, Events)   │                                  │
│                    └───────────────────────┘                                  │
└───────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                           MAYAN CORE (Untouched)                              │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │   /api/v4/ - Original REST API (Documents, Cabinets, Search, etc.)      │ │
│  │   (Используется напрямую для неизмененных операций)                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Ключевые Принципы BFF

1. **НЕ модифицируем core Mayan код** — все изменения в отдельном Django app
2. **Sidecar App Pattern** — `headless_api` живет рядом с Mayan, но изолирован
3. **Progressive Enhancement** — сначала закрываем критические gaps, потом расширяем
4. **Backward Compatible** — старые endpoints продолжают работать

---

## 3. Фазы Реализации BFF-Адаптера

### Phase B-Adapter: Headless API Layer (Недели 1-4)

**Цель:** Создать недостающие endpoints для SPA self-service функционала.

> Реалистичная корректировка сроков: +2 недели к плану V3 из-за подтверждённых CRITICAL FAILURE (400/404/401) по TEST_EXECUTION_REPORT.md.

#### Task B.1: HeadlessPasswordView (Исправляет TC-AUTH-02)

**Проблема:** POST `/api/v4/users/current/password/` возвращает 404

**Решение:** Создать endpoint `POST /api/v4/headless/password/change/`

**Техническая Спецификация:**

```python
# mayan/apps/headless_api/views/password_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

class HeadlessPasswordChangeView(APIView):
    """
    REST API endpoint для смены пароля.
    
    Mayan EDMS не предоставляет этот функционал через REST API.
    Этот view обходит ограничение, напрямую вызывая Django auth.
    
    ВАЖНО: Мы НЕ используем сессии. Мы проверяем request.user
    из Token authentication и вызываем set_password() напрямую.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Смена пароля пользователя.
        
        Ожидаемый JSON:
        {
            "current_password": "старый_пароль",
            "new_password": "новый_пароль",
            "new_password_confirm": "новый_пароль"
        }
        
        Логика:
        1. Проверяем, что current_password совпадает с текущим
        2. Проверяем, что new_password == new_password_confirm
        3. Валидируем new_password (минимум 8 символов, не только цифры)
        4. Вызываем user.set_password(new_password)
        5. Сохраняем пользователя
        6. Возвращаем success или error
        
        Безопасность:
        - Токен пользователя НЕ инвалидируется (текущая сессия продолжает работать)
        - Логируем событие смены пароля в Mayan Events
        """
        user = request.user
        data = request.data
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        new_password_confirm = data.get('new_password_confirm')
        
        # Валидация входных данных
        if not all([current_password, new_password, new_password_confirm]):
            return Response(
                {'error': 'Все поля обязательны', 'error_code': 'MISSING_FIELDS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка текущего пароля
        if not check_password(current_password, user.password):
            return Response(
                {'error': 'Неверный текущий пароль', 'error_code': 'INVALID_CURRENT_PASSWORD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка совпадения новых паролей
        if new_password != new_password_confirm:
            return Response(
                {'error': 'Пароли не совпадают', 'error_code': 'PASSWORD_MISMATCH'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация сложности пароля
        if len(new_password) < 8:
            return Response(
                {'error': 'Пароль должен содержать минимум 8 символов', 'error_code': 'PASSWORD_TOO_SHORT'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password.isdigit():
            return Response(
                {'error': 'Пароль не может состоять только из цифр', 'error_code': 'PASSWORD_NUMERIC_ONLY'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Установка нового пароля
        user.set_password(new_password)
        user.save()
        
        # Логирование события (опционально, для Mayan Events)
        # event = Event(
        #     actor=user,
        #     action='password_changed',
        #     target=user
        # )
        # event.save()
        
        return Response(
            {'message': 'Пароль успешно изменен', 'status': 'success'},
            status=status.HTTP_200_OK
        )
```

**URL конфигурация:**

```python
# mayan/apps/headless_api/urls.py

from django.urls import path
from .views.password_views import HeadlessPasswordChangeView

app_name = 'headless_api'

urlpatterns = [
    path(
        'password/change/',
        HeadlessPasswordChangeView.as_view(),
        name='password-change'
    ),
]
```

**Регистрация в Mayan:**

```python
# mayan/apps/headless_api/apps.py

from django.apps import AppConfig

class HeadlessApiConfig(AppConfig):
    name = 'mayan.apps.headless_api'
    verbose_name = 'Headless API'
    
    def ready(self):
        # Регистрируем app в REST API namespace
        pass
```

```python
# mayan/urls.py (или соответствующий корневой urls.py)
# Добавить в urlpatterns:

urlpatterns += [
    path('api/v4/headless/', include('mayan.apps.headless_api.urls')),
]
```

**Валидация:**
- POST `/api/v4/headless/password/change/` с валидным токеном → 200 OK
- POST без токена → 401 Unauthorized
- POST с неверным current_password → 400 Bad Request

---

#### Task B.2: HeadlessConfigView (Исправляет TC-UPLOAD-02)

**Проблема:** Фронтенд не знает, какие поля обязательны при загрузке документа. document_type_id хардкодится без понимания требований.

**Решение:** Создать endpoint `GET /api/v4/headless/config/document_types/{id}/`

**Техническая Спецификация:**

```python
# mayan/apps/headless_api/views/config_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import MetadataType, DocumentTypeMetadataType

class HeadlessDocumentTypeConfigView(APIView):
    """
    Экспозиция конфигурации DocumentType для динамических форм.
    
    Mayan API возвращает только базовую информацию о типах документов.
    Этот endpoint предоставляет полную конфигурацию:
    - Обязательные поля метаданных
    - Правила валидации
    - Доступные workflow
    - Настройки retention
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_type_id=None):
        """
        Получить конфигурацию типа документа.
        
        Если document_type_id не указан, возвращает все типы.
        
        Возвращаемый JSON:
        {
            "id": 1,
            "label": "Изображение",
            "description": "Фотографии и графика",
            "required_metadata": [
                {
                    "id": 5,
                    "name": "author",
                    "label": "Автор",
                    "type": "text",
                    "required": true,
                    "validation_regex": null,
                    "default_value": null
                },
                {
                    "id": 7,
                    "name": "copyright",
                    "label": "Авторские права",
                    "type": "text",
                    "required": true,
                    "validation_regex": "^©.*$",
                    "default_value": "© 2025"
                }
            ],
            "optional_metadata": [...],
            "workflows": [
                {
                    "id": 1,
                    "label": "Модерация изображений",
                    "initial_state": "pending_review"
                }
            ],
            "retention_policy": {
                "enabled": true,
                "days": 365
            },
            "ocr_enabled": true,
            "ai_analysis_enabled": true
        }
        """
        if document_type_id:
            try:
                doc_type = DocumentType.objects.get(pk=document_type_id)
                return Response(self._serialize_document_type(doc_type))
            except DocumentType.DoesNotExist:
                return Response(
                    {'error': 'Тип документа не найден', 'error_code': 'NOT_FOUND'},
                    status=404
                )
        else:
            doc_types = DocumentType.objects.all()
            return Response([
                self._serialize_document_type(dt) for dt in doc_types
            ])
    
    def _serialize_document_type(self, doc_type):
        """Сериализация полной конфигурации типа документа."""
        
        # Получаем связанные метаданные
        metadata_relations = DocumentTypeMetadataType.objects.filter(
            document_type=doc_type
        ).select_related('metadata_type')
        
        required_metadata = []
        optional_metadata = []
        
        for relation in metadata_relations:
            meta = relation.metadata_type
            meta_dict = {
                'id': meta.pk,
                'name': meta.name,
                'label': meta.label,
                'type': self._get_metadata_type(meta),
                'required': relation.required,
                'validation_regex': getattr(meta, 'validation', None),
                'default_value': getattr(meta, 'default', None),
            }
            
            if relation.required:
                required_metadata.append(meta_dict)
            else:
                optional_metadata.append(meta_dict)
        
        # Получаем workflow (если доступны)
        workflows = []
        if hasattr(doc_type, 'workflows'):
            for wf in doc_type.workflows.all():
                workflows.append({
                    'id': wf.pk,
                    'label': wf.label,
                    'initial_state': getattr(wf, 'initial_state', {}).get('label', 'unknown')
                })
        
        return {
            'id': doc_type.pk,
            'label': doc_type.label,
            'description': getattr(doc_type, 'description', ''),
            'required_metadata': required_metadata,
            'optional_metadata': optional_metadata,
            'workflows': workflows,
            'retention_policy': {
                'enabled': getattr(doc_type, 'delete_time_period', None) is not None,
                'days': getattr(doc_type, 'delete_time_period', None) or 0
            },
            'ocr_enabled': getattr(doc_type, 'ocr', True),
            'ai_analysis_enabled': True  # DAM расширение
        }
    
    def _get_metadata_type(self, meta):
        """Определение типа поля для фронтенда."""
        # Логика определения типа на основе validation и других свойств
        if hasattr(meta, 'lookup'):
            return 'select'
        return 'text'
```

**URL конфигурация:**

```python
# mayan/apps/headless_api/urls.py (дополнение)

urlpatterns += [
    path(
        'config/document_types/',
        HeadlessDocumentTypeConfigView.as_view(),
        name='config-document-types-list'
    ),
    path(
        'config/document_types/<int:document_type_id>/',
        HeadlessDocumentTypeConfigView.as_view(),
        name='config-document-type-detail'
    ),
]
```

**Валидация:**
- GET `/api/v4/headless/config/document_types/` → Список всех типов с конфигурацией
- GET `/api/v4/headless/config/document_types/1/` → Детальная конфигурация типа 1
- Фронтенд строит динамическую форму на основе `required_metadata`

---

#### Task B.3: HeadlessActivityFeedView (Исправляет TC-ACT-01)

**Проблема:** `/api/v4/events/` возвращает ВСЕ системные события, а не персонализированную ленту пользователя.

**Решение:** Создать endpoint `GET /api/v4/headless/activity/feed/`

**Техническая Спецификация:**

```python
# mayan/apps/headless_api/views/activity_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from mayan.apps.events.models import StoredEventType
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from mayan.apps.documents.models import Document

class ActivityFeedPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class HeadlessActivityFeedView(APIView):
    """
    Персонализированная лента активности пользователя.
    
    В отличие от /api/v4/events/, этот endpoint возвращает только:
    - События, инициированные текущим пользователем
    - События, связанные с документами, к которым пользователь имеет доступ
    - Отформатированные для UI (читаемые описания, временные метки)
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ActivityFeedPagination
    
    def get(self, request):
        """
        Получить ленту активности пользователя.
        
        Query параметры:
        - page: номер страницы (default: 1)
        - page_size: размер страницы (default: 20, max: 100)
        - filter: тип фильтра ('my_actions', 'my_documents', 'all')
        
        Возвращаемый JSON:
        {
            "count": 150,
            "next": "/api/v4/headless/activity/feed/?page=2",
            "previous": null,
            "results": [
                {
                    "id": 1234,
                    "timestamp": "2025-12-04T15:33:06Z",
                    "actor": {
                        "id": 1,
                        "username": "admin",
                        "full_name": "Administrator"
                    },
                    "verb": "загрузил",
                    "action_type": "document_upload",
                    "target": {
                        "id": 567,
                        "type": "document",
                        "label": "Отчет Q4.pdf"
                    },
                    "description": "Пользователь admin загрузил документ 'Отчет Q4.pdf'"
                },
                ...
            ]
        }
        """
        user = request.user
        filter_type = request.query_params.get('filter', 'my_actions')
        
        # Базовый queryset
        if filter_type == 'my_actions':
            # Только действия текущего пользователя
            actions = Action.objects.filter(actor_object_id=user.pk)
        elif filter_type == 'my_documents':
            # Действия с документами пользователя
            document_ct = ContentType.objects.get_for_model(Document)
            user_doc_ids = Document.objects.filter(
                # Документы, загруженные пользователем или с доступом
                # (упрощенная логика, в продакшене нужна ACL проверка)
            ).values_list('id', flat=True)
            actions = Action.objects.filter(
                target_content_type=document_ct,
                target_object_id__in=user_doc_ids
            )
        else:
            # Все доступные события (с пагинацией)
            actions = Action.objects.all()
        
        actions = actions.order_by('-timestamp')[:100]  # Лимит для производительности
        
        # Сериализация
        results = []
        for action in actions:
            results.append({
                'id': action.pk,
                'timestamp': action.timestamp.isoformat(),
                'actor': self._serialize_actor(action.actor),
                'verb': self._translate_verb(action.verb),
                'action_type': action.verb,
                'target': self._serialize_target(action.target),
                'description': self._build_description(action)
            })
        
        return Response({
            'count': len(results),
            'next': None,  # Упрощенная пагинация
            'previous': None,
            'results': results
        })
    
    def _serialize_actor(self, actor):
        if not actor:
            return None
        return {
            'id': actor.pk,
            'username': getattr(actor, 'username', 'system'),
            'full_name': getattr(actor, 'get_full_name', lambda: '')()
        }
    
    def _serialize_target(self, target):
        if not target:
            return None
        return {
            'id': target.pk,
            'type': target._meta.model_name,
            'label': str(target)
        }
    
    def _translate_verb(self, verb):
        """Перевод verb в читаемый текст."""
        translations = {
            'document_create': 'создал документ',
            'document_upload': 'загрузил',
            'document_edit': 'изменил',
            'document_delete': 'удалил',
            'document_download': 'скачал',
            'document_view': 'просмотрел',
            'tag_attach': 'добавил тег',
            'tag_remove': 'удалил тег',
            'metadata_edit': 'изменил метаданные',
        }
        return translations.get(verb, verb)
    
    def _build_description(self, action):
        """Построение читаемого описания."""
        actor_name = getattr(action.actor, 'username', 'Система')
        verb = self._translate_verb(action.verb)
        target = str(action.target) if action.target else ''
        return f"Пользователь {actor_name} {verb} '{target}'"
```

**URL конфигурация:**

```python
# mayan/apps/headless_api/urls.py (дополнение)

urlpatterns += [
    path(
        'activity/feed/',
        HeadlessActivityFeedView.as_view(),
        name='activity-feed'
    ),
]
```

**Валидация:**
- GET `/api/v4/headless/activity/feed/` → Персонализированная лента
- GET `/api/v4/headless/activity/feed/?filter=my_documents` → Только события с документами пользователя

---

## 4. Обновленный Timeline

### 4.1 Фазы Реализации

```
Неделя 1-2  │████████████████│ B.1: HeadlessPasswordView
            │                │ - Реализация endpoint
            │                │ - Юнит-тесты
            │       ▼        │ CHECKPOINT: Смена пароля работает

Неделя 3    │████████████████│ B.2: HeadlessConfigView  
            │                │ - Экспозиция метаданных
            │                │ - Динамические формы
            │       ▼        │ CHECKPOINT: Формы загрузки динамические

Неделя 4    │████████████████│ B.3: HeadlessActivityFeedView
            │                │ - Персонализированная лента
            │                │ - Интеграция с фронтендом
            │       ▼        │ CHECKPOINT: Activity feed работает

Неделя 5-6  │████████████████│ A-Refactor: Frontend URL Migration
            │                │ - authService → /headless/password/
            │                │ - uploadService → /headless/config/
            │                │ - dashboardService → /headless/activity/
            │       ▼        │ CHECKPOINT: Фронтенд интегрирован

Неделя 7-8  │████████████████│ Integration Testing & Polish
            │                │ - E2E тесты
            │                │ - Performance optimization
            │                │ - Security audit
            │       ▼        │ PRODUCTION READY
```

### 4.2 Milestones

| Milestone | Неделя | Критерий Успеха |
|-----------|--------|-----------------|
| **M1: Password Change** | 2 | POST /headless/password/change/ работает |
| **M2: Config Exposure** | 3 | Формы загрузки строятся динамически |
| **M3: Activity Feed** | 4 | Dashboard показывает реальную активность |
| **M4: Full Integration** | 6 | Все фронтенд сервисы используют headless API |
| **M5: Production** | 8 | Развертывание в production |

---

## 5. Risk Register (Обновленный)

| Риск | Вероятность | Влияние | Митигация | Статус |
|------|-------------|---------|-----------|--------|
| **Mayan upgrade breaks headless_api** | Средняя | Высокое | Версионирование, изоляция кода | 🟡 Мониторинг |
| **Performance degradation** | Низкая | Среднее | Кеширование, оптимизация запросов | 🟢 Планируется |
| **Security vulnerabilities** | Низкая | Критическое | Code review, security audit | 🟢 Планируется |
| **Token invalidation on password change** | Средняя | Низкое | Документация, опциональный логаут | 🟢 Решено в spec |

---

## 6. Definition of Done (Обновленный)

### 6.1 Feature DoD для BFF

Фича считается "Готовой" когда:

- [x] Python код написан и проходит линтинг (flake8)
- [x] Unit тесты покрывают >80% кода
- [x] Integration тест с реальным Mayan работает
- [x] API документирован в OpenAPI spec
- [x] Frontend сервис обновлен для использования нового endpoint
- [x] E2E тест проходит (Playwright/Cypress)
- [x] Security review проведен
- [x] PR одобрен и смержен

### 6.2 Production DoD

- [ ] Все BFF endpoints развернуты
- [ ] Фронтенд использует headless API
- [ ] Load testing пройден (100 concurrent users)
- [ ] Security audit пройден
- [ ] Monitoring настроен (Sentry, Prometheus)
- [ ] Документация обновлена
- [ ] Stakeholder sign-off получен

---

## 📋 Связанная Документация

- **[BACKEND_ANALYSIS_V4.md](BACKEND_ANALYSIS_V4.md)** — Детальная архитектура headless_api
- **[FRONTEND_ANALYSIS_V4.md](FRONTEND_ANALYSIS_V4.md)** — План рефакторинга фронтенда
- **[TEST_EXECUTION_REPORT.md](TEST_EXECUTION_REPORT.md)** — Доказательства API сбоев
- **[API_TEST_PLAN.md](API_TEST_PLAN.md)** — План тестирования
- **[ARCHITECTURE_GAP_REPORT_V2.md](ARCHITECTURE_GAP_REPORT_V2.md)** — Анализ архитектурных ограничений

---

**Версия документа:** 4.0 (Архитектурный Пивот — BFF Стратегия)
**Создан:** 04 декабря 2025
**Автор:** Lead Technical Architect

---

*🚨 КРИТИЧЕСКИЙ ПЕРЕСМОТР: Стратегия V3 "Прямой Интеграции" признана несостоятельной. Переход на BFF-адаптер обязателен для достижения production-ready статуса.*


