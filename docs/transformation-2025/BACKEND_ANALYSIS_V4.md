# Анализ Бэкенда V4 — Prime-EDMS / DAM System

**Дата анализа:** 04 декабря 2025
**Версия:** 4.0 (КРИТИЧЕСКИЙ ПЕРЕСМОТР — Headless API Micro-App Strategy)
**Автор:** Senior System Analyst & Backend Architect
**Coverage:** Mayan EDMS Limitations, Headless API Architecture, Implementation Specs

---

## 📋 Содержание

1. [Критический Статус](#1-критический-статус)
2. [Доказательства API Сбоев](#2-доказательства-api-сбоев)
3. [Архитектурные Ограничения Mayan](#3-архитектурные-ограничения-mayan)
4. [Новая Архитектура: Headless API Micro-App](#4-новая-архитектура-headless-api-micro-app)
5. [Детальные Спецификации Endpoints](#5-детальные-спецификации-endpoints)
6. [Структура Кода Headless API](#6-структура-кода-headless-api)
7. [Интеграция с Mayan Core](#7-интеграция-с-mayan-core)
8. [Тестирование и Валидация](#8-тестирование-и-валидация)

---

## 1. Критический Статус

### 🚨 КРИТИЧЕСКИЙ СБОЙ: Прямая SPA-Интеграция Невозможна

**Предыдущий статус (V3):** "100% Integration Complete — Production Ready"

**Реальный статус (V4):** 🔴 **АРХИТЕКТУРНОЕ ОГРАНИЧЕНИЕ** — Mayan EDMS API не предоставляет необходимые self-service endpoints для SPA.

### Резюме Проблем

| Функционал | Ожидание Фронтенда | Реальность Mayan API | Статус |
|------------|-------------------|---------------------|--------|
| **Смена пароля** | POST /api/v4/users/current/password/ | ❌ Endpoint НЕ существует | 🔴 КРИТИЧЕСКИЙ СБОЙ |
| **Конфигурация типов** | GET /api/v4/document_types/{id}/config/ | ❌ Только базовая информация | 🔴 КРИТИЧЕСКИЙ СБОЙ |
| **Персональная лента** | GET /api/v4/activity/me/ | ❌ Только системные события | 🟡 ОГРАНИЧЕНИЕ |
| **Сброс пароля** | POST /api/v4/auth/password/reset/ | ❌ Только HTML форма | 🔴 КРИТИЧЕСКИЙ СБОЙ |

---

## 2. Доказательства API Сбоев

### 2.1 Тест Смены Пароля (TC-AUTH-02)

**Дата выполнения:** 04 декабря 2025, 15:33:06 UTC
**Инструмент:** Python requests library
**Скрипт:** `tests/verification_script.py`

```
==================================================
TEST 2: PASSWORD CHANGE - POST /api/v4/users/current/password/
==================================================
URL: http://127.0.0.1:8080/api/v4/users/current/password/
Headers: {'Content-Type': 'application/json', 'Accept': 'application/json'}
Payload: {
  "new_password": "newpassword123"
}
Status Code: 404
Response Headers: {
  'Server': 'gunicorn',
  'Content-Type': 'text/html; charset=utf-8',
  'Content-Length': '2484'
}
Response: HTML страница "Page not found"
```

**Вердикт:** 🔴 **ENDPOINT НЕ СУЩЕСТВУЕТ**

### 2.2 Анализ Mayan UserSerializer

**Файл:** `mayan/apps/user_management/serializers.py`

```python
# Актуальный код Mayan UserSerializer
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = (
            'id', 'url', 'username', 'first_name', 'last_name', 
            'email', 'groups', 'is_active', 'is_staff', 'is_superuser'
        )
        # ОБРАТИТЕ ВНИМАНИЕ: 'password' НЕ включен в fields!
```

**Вердикт:** 🔴 **PATCH /api/v4/users/current/ НЕ ПОДДЕРЖИВАЕТ изменение пароля**

Документация V3 утверждала: "Используйте PATCH с полем password"
Реальность: `password` **НЕ ЯВЛЯЕТСЯ** writable field в UserSerializer.

### 2.3 Анализ Mayan Password Views

**Файл:** `mayan/apps/authentication/views.py`

```python
class MayanPasswordChangeView(PasswordChangeView):
    """
    HTML-based password change view.
    Наследует от django.contrib.auth.views.PasswordChangeView
    Рендерит HTML форму, НЕ принимает JSON.
    """
    extra_context = {'title': _('Password change')}
    success_url = reverse_lazy('user_management:current_user_details')
```

**Вердикт:** 🔴 **Смена пароля доступна ТОЛЬКО через HTML форму**

---

## 3. Архитектурные Ограничения Mayan

### 3.1 Философия Mayan API

Mayan EDMS API был спроектирован с следующими предположениями:

1. **Автоматизация:** API предназначен для скриптов, CI/CD, интеграций с другими системами
2. **Backend-to-Backend:** Предполагается, что клиент — это другой сервер, а не браузер
3. **Django Admin UI:** Self-service функции доступны через Django Admin или специальные HTML views
4. **Сессионная аутентификация:** Многие операции предполагают Django session, а не stateless tokens

### 3.2 Отсутствующие Self-Service Endpoints

| Категория | Функция | Mayan HTML | Mayan REST | Необходимо для SPA |
|-----------|---------|------------|------------|-------------------|
| **Auth** | Смена пароля | ✅ /authentication/password/change/ | ❌ | ✅ Критично |
| **Auth** | Сброс пароля | ✅ /authentication/password/reset/ | ❌ | ✅ Критично |
| **Auth** | 2FA управление | ✅ Django Admin | ❌ | 🟡 Желательно |
| **Profile** | Редактирование профиля | ✅ /user_management/user/edit/ | ❌ Частично (без пароля) | ✅ Критично |
| **Config** | Конфигурация типов документов | ✅ Django Admin | ❌ Только базовая информация | ✅ Критично |
| **Activity** | Персональная лента | ❌ | ❌ | 🟡 Желательно |

### 3.3 Ограничения Exposure Конфигурации

**Проблема:** Фронтенд не может строить динамические формы загрузки.

**Пример:** При загрузке документа типа "Изображение" требуется заполнить поля:
- `author` (обязательно)
- `copyright` (обязательно, regex: `^©.*$`)
- `description` (опционально)

**Текущий API ответ:**
```json
GET /api/v4/document_types/1/
{
  "id": 1,
  "label": "Изображение",
  "description": "Фотографии и графика",
  "url": "http://localhost:8080/api/v4/document_types/1/"
}
```

**Необходимый API ответ:**
```json
GET /api/v4/headless/config/document_types/1/
{
  "id": 1,
  "label": "Изображение",
  "description": "Фотографии и графика",
  "required_metadata": [
    {"name": "author", "label": "Автор", "type": "text", "required": true},
    {"name": "copyright", "label": "©", "type": "text", "required": true, "validation_regex": "^©.*$"}
  ],
  "optional_metadata": [
    {"name": "description", "label": "Описание", "type": "textarea", "required": false}
  ],
  "workflows": [...],
  "retention_policy": {...}
}
```

---

## 4. Новая Архитектура: Headless API Micro-App

### 4.1 Концепция Sidecar App

**Принцип:** Мы **НЕ модифицируем** core Mayan код. Вместо этого создаем отдельное Django приложение `headless_api`, которое:

1. **Изолировано** от Mayan core
2. **Расширяет** функционал через внутренние Django/Mayan API
3. **Не блокирует** обновления Mayan EDMS
4. **Легко удаляется** при необходимости

### 4.2 Архитектурная Диаграмма

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DJANGO PROJECT (mayan)                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    MAYAN CORE APPS (Untouched)                       │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │  documents   │  │   metadata   │  │   events     │               │   │
│  │  │              │  │              │  │              │               │   │
│  │  │  Document    │  │ MetadataType │  │   Event      │               │   │
│  │  │  DocumentFile│  │ Metadata     │  │   Action     │               │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │ user_mgmt    │  │ authentication│ │  rest_api    │               │   │
│  │  │              │  │              │  │              │               │   │
│  │  │  User        │  │ TokenAuth    │  │  DRF Router  │               │   │
│  │  │  Group       │  │ Session      │  │  Permissions │               │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │   │
│  │                                                                      │   │
│  │  /api/v4/documents/    /api/v4/users/    /api/v4/events/            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                         │                                   │
│                                         │ Django Internal Imports           │
│                                         ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              🆕 HEADLESS_API APP (New Sidecar)                       │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │                        views/                                   │ │   │
│  │  │                                                                 │ │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │ │   │
│  │  │  │ password_views.py│  │ config_views.py  │  │activity_views│ │ │   │
│  │  │  │                  │  │                  │  │              │ │ │   │
│  │  │  │ HeadlessPassword │  │ HeadlessConfig   │  │ HeadlessAct  │ │ │   │
│  │  │  │   ChangeView     │  │   View           │  │   FeedView   │ │ │   │
│  │  │  │                  │  │                  │  │              │ │ │   │
│  │  │  │ user.set_password│  │ DocumentType     │  │ Action.objects│ │   │
│  │  │  │ (Django Auth)    │  │ .metadata_types  │  │ .filter(actor)│ │   │
│  │  │  └──────────────────┘  └──────────────────┘  └──────────────┘ │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  /api/v4/headless/password/    /api/v4/headless/config/            │   │
│  │  /api/v4/headless/activity/                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Ключевые Принципы

1. **Импорты, а не Модификации:**
   ```python
   # ✅ Правильно: Импортируем из Mayan
   from mayan.apps.documents.models import DocumentType
   from mayan.apps.user_management.models import User
   
   # ❌ Неправильно: Модифицируем Mayan код
   # Редактирование mayan/apps/documents/models.py
   ```

2. **Отдельный URL Namespace:**
   ```python
   # Все headless endpoints живут в /api/v4/headless/
   # Не конфликтуют с Mayan /api/v4/
   ```

3. **Собственные Сериализаторы:**
   ```python
   # Не наследуем от Mayan сериализаторов
   # Создаем свои, заточенные под SPA
   ```

4. **Независимые Миграции:**
   ```python
   # Если нужны свои модели (кеш, логи)
   # Миграции в headless_api/migrations/
   ```

---

## 5. Детальные Спецификации Endpoints

### 5.1 POST /api/v4/headless/password/change/

**Назначение:** Смена пароля текущего пользователя через REST API.

**Почему Mayan не предоставляет:**
- Mayan использует Django `PasswordChangeView` (HTML)
- UserSerializer не включает `password` в writable fields
- Философия "админ меняет пароли через Django Admin"

**Наша реализация:**

```python
# mayan/apps/headless_api/views/password_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)

class HeadlessPasswordChangeView(APIView):
    """
    REST API endpoint для смены пароля.
    
    Endpoint: POST /api/v4/headless/password/change/
    
    Headers:
        Authorization: Token <token>
        Content-Type: application/json
    
    Request Body:
        {
            "current_password": "string",
            "new_password": "string",
            "new_password_confirm": "string"
        }
    
    Responses:
        200 OK: {"message": "Пароль успешно изменен", "status": "success"}
        400 Bad Request: {"error": "...", "error_code": "..."}
        401 Unauthorized: {"detail": "Authentication credentials were not provided."}
    
    Логика:
        1. Проверяем токен (DRF IsAuthenticated)
        2. Валидируем current_password
        3. Валидируем new_password по Django правилам
        4. Сохраняем новый пароль
        5. НЕ инвалидируем токен (текущая сессия продолжает работать)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        data = request.data
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        new_password_confirm = data.get('new_password_confirm', '')
        
        # Валидация: все поля обязательны
        if not all([current_password, new_password, new_password_confirm]):
            return Response(
                {
                    'error': 'Все поля обязательны: current_password, new_password, new_password_confirm',
                    'error_code': 'MISSING_FIELDS'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка текущего пароля
        if not check_password(current_password, user.password):
            logger.warning(f"Password change failed for user {user.username}: invalid current password")
            return Response(
                {
                    'error': 'Неверный текущий пароль',
                    'error_code': 'INVALID_CURRENT_PASSWORD'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка совпадения новых паролей
        if new_password != new_password_confirm:
            return Response(
                {
                    'error': 'Новые пароли не совпадают',
                    'error_code': 'PASSWORD_MISMATCH'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация нового пароля по Django правилам
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {
                    'error': '; '.join(e.messages),
                    'error_code': 'PASSWORD_VALIDATION_FAILED',
                    'details': e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Установка нового пароля
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password changed successfully for user {user.username}")
        
        return Response(
            {
                'message': 'Пароль успешно изменен',
                'status': 'success'
            },
            status=status.HTTP_200_OK
        )
```

### 5.2 GET /api/v4/headless/config/document_types/

**Назначение:** Экспозиция полной конфигурации типов документов для динамических форм.

**Почему Mayan не предоставляет:**
- DocumentTypeSerializer возвращает только label, description, url
- Метаданные требуют отдельных запросов к /metadata_types/
- Required/optional статус не экспонируется
- Валидационные правила недоступны

**Наша реализация:**

```python
# mayan/apps/headless_api/views/config_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import DocumentTypeMetadataType

class HeadlessDocumentTypeConfigView(APIView):
    """
    Экспозиция конфигурации DocumentType для SPA форм.
    
    Endpoint: GET /api/v4/headless/config/document_types/
    Endpoint: GET /api/v4/headless/config/document_types/{id}/
    
    Response Schema:
        {
            "id": int,
            "label": string,
            "description": string,
            "required_metadata": [
                {
                    "id": int,
                    "name": string,
                    "label": string,
                    "type": "text" | "number" | "date" | "select",
                    "required": true,
                    "validation_regex": string | null,
                    "default_value": string | null,
                    "options": [string] | null  // для type="select"
                }
            ],
            "optional_metadata": [...],
            "workflows": [
                {
                    "id": int,
                    "label": string,
                    "initial_state": string
                }
            ],
            "retention_policy": {
                "enabled": bool,
                "days": int
            },
            "capabilities": {
                "ocr_enabled": bool,
                "ai_analysis_enabled": bool,
                "preview_enabled": bool
            }
        }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_type_id=None):
        if document_type_id:
            try:
                doc_type = DocumentType.objects.get(pk=document_type_id)
                return Response(self._serialize_full(doc_type))
            except DocumentType.DoesNotExist:
                return Response(
                    {'error': 'Тип документа не найден', 'error_code': 'NOT_FOUND'},
                    status=404
                )
        else:
            # Список всех типов с базовой информацией
            doc_types = DocumentType.objects.all()
            return Response([
                self._serialize_basic(dt) for dt in doc_types
            ])
    
    def _serialize_basic(self, doc_type):
        """Базовая информация для списка."""
        return {
            'id': doc_type.pk,
            'label': doc_type.label,
            'description': getattr(doc_type, 'description', ''),
            'url': f'/api/v4/headless/config/document_types/{doc_type.pk}/'
        }
    
    def _serialize_full(self, doc_type):
        """Полная конфигурация для формы."""
        # Получаем метаданные
        metadata_relations = DocumentTypeMetadataType.objects.filter(
            document_type=doc_type
        ).select_related('metadata_type')
        
        required_metadata = []
        optional_metadata = []
        
        for relation in metadata_relations:
            meta = relation.metadata_type
            meta_dict = self._serialize_metadata(meta, relation.required)
            
            if relation.required:
                required_metadata.append(meta_dict)
            else:
                optional_metadata.append(meta_dict)
        
        # Получаем workflows
        workflows = self._get_workflows(doc_type)
        
        return {
            'id': doc_type.pk,
            'label': doc_type.label,
            'description': getattr(doc_type, 'description', ''),
            'required_metadata': required_metadata,
            'optional_metadata': optional_metadata,
            'workflows': workflows,
            'retention_policy': {
                'enabled': hasattr(doc_type, 'delete_time_period') and doc_type.delete_time_period,
                'days': getattr(doc_type, 'delete_time_period', 0) or 0
            },
            'capabilities': {
                'ocr_enabled': getattr(doc_type, 'ocr', True),
                'ai_analysis_enabled': True,  # DAM extension
                'preview_enabled': True
            }
        }
    
    def _serialize_metadata(self, meta, required):
        """Сериализация метаданных с типом поля."""
        return {
            'id': meta.pk,
            'name': meta.name,
            'label': meta.label,
            'type': self._infer_field_type(meta),
            'required': required,
            'validation_regex': getattr(meta, 'validation', None),
            'default_value': getattr(meta, 'default', None),
            'options': self._get_lookup_options(meta)
        }
    
    def _infer_field_type(self, meta):
        """Определение типа поля для фронтенда."""
        if hasattr(meta, 'lookup') and meta.lookup:
            return 'select'
        validation = getattr(meta, 'validation', '') or ''
        if 'date' in validation.lower():
            return 'date'
        if validation.startswith('^[0-9'):
            return 'number'
        return 'text'
    
    def _get_lookup_options(self, meta):
        """Получение опций для select полей."""
        if hasattr(meta, 'lookup') and meta.lookup:
            # Парсинг lookup значений
            return meta.lookup.split('\n') if meta.lookup else None
        return None
    
    def _get_workflows(self, doc_type):
        """Получение связанных workflows."""
        workflows = []
        if hasattr(doc_type, 'workflows'):
            for wf in doc_type.workflows.all():
                initial_state = None
                if hasattr(wf, 'get_initial_state'):
                    state = wf.get_initial_state()
                    initial_state = state.label if state else None
                workflows.append({
                    'id': wf.pk,
                    'label': wf.label,
                    'initial_state': initial_state
                })
        return workflows
```

### 5.3 GET /api/v4/headless/activity/feed/

**Назначение:** Персонализированная лента активности пользователя.

**Почему Mayan не предоставляет:**
- /api/v4/events/ возвращает ВСЕ системные события
- Нет фильтрации по actor (текущий пользователь)
- Нет человекочитаемых описаний
- Нет группировки по типам

**Наша реализация:**

```python
# mayan/apps/headless_api/views/activity_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from mayan.apps.documents.models import Document

class HeadlessActivityFeedView(APIView):
    """
    Персонализированная лента активности.
    
    Endpoint: GET /api/v4/headless/activity/feed/
    
    Query Parameters:
        page: int (default: 1)
        page_size: int (default: 20, max: 100)
        filter: 'my_actions' | 'my_documents' | 'all' (default: 'my_actions')
    
    Response Schema:
        {
            "count": int,
            "page": int,
            "page_size": int,
            "results": [
                {
                    "id": int,
                    "timestamp": "ISO8601",
                    "actor": {
                        "id": int,
                        "username": string,
                        "full_name": string
                    },
                    "verb": string,  // Русский перевод
                    "verb_code": string,  // Оригинальный код
                    "target": {
                        "id": int,
                        "type": string,
                        "label": string,
                        "url": string | null
                    },
                    "description": string  // Полное описание
                }
            ]
        }
    """
    permission_classes = [IsAuthenticated]
    
    # Переводы verb
    VERB_TRANSLATIONS = {
        'document created': 'создал документ',
        'document edited': 'изменил документ',
        'document deleted': 'удалил документ',
        'document downloaded': 'скачал документ',
        'document viewed': 'просмотрел документ',
        'file uploaded': 'загрузил файл',
        'tag attached': 'добавил тег',
        'tag removed': 'удалил тег',
        'metadata edited': 'изменил метаданные',
        'cabinet document added': 'добавил в коллекцию',
        'cabinet document removed': 'удалил из коллекции',
        'workflow transition': 'изменил статус',
        'user logged in': 'вошел в систему',
        'user logged out': 'вышел из системы',
    }
    
    def get(self, request):
        user = request.user
        filter_type = request.query_params.get('filter', 'my_actions')
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        # Базовый queryset
        actions = self._get_filtered_actions(user, filter_type)
        
        # Пагинация
        total_count = actions.count()
        offset = (page - 1) * page_size
        actions = actions[offset:offset + page_size]
        
        # Сериализация
        results = [self._serialize_action(action) for action in actions]
        
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'results': results
        })
    
    def _get_filtered_actions(self, user, filter_type):
        """Фильтрация действий по типу."""
        if filter_type == 'my_actions':
            # Только действия текущего пользователя
            return Action.objects.filter(
                actor_object_id=user.pk
            ).order_by('-timestamp')
        
        elif filter_type == 'my_documents':
            # Действия с документами, доступными пользователю
            # Упрощенная логика - в продакшене нужна ACL проверка
            document_ct = ContentType.objects.get_for_model(Document)
            return Action.objects.filter(
                target_content_type=document_ct
            ).order_by('-timestamp')
        
        else:  # 'all'
            return Action.objects.all().order_by('-timestamp')
    
    def _serialize_action(self, action):
        """Сериализация одного действия."""
        return {
            'id': action.pk,
            'timestamp': action.timestamp.isoformat(),
            'actor': self._serialize_actor(action.actor),
            'verb': self.VERB_TRANSLATIONS.get(action.verb, action.verb),
            'verb_code': action.verb,
            'target': self._serialize_target(action.target),
            'description': self._build_description(action)
        }
    
    def _serialize_actor(self, actor):
        if not actor:
            return {'id': None, 'username': 'system', 'full_name': 'Система'}
        return {
            'id': actor.pk,
            'username': getattr(actor, 'username', 'unknown'),
            'full_name': getattr(actor, 'get_full_name', lambda: '')() or actor.username
        }
    
    def _serialize_target(self, target):
        if not target:
            return None
        return {
            'id': target.pk,
            'type': target._meta.model_name,
            'label': str(target),
            'url': getattr(target, 'get_absolute_url', lambda: None)()
        }
    
    def _build_description(self, action):
        """Построение полного описания."""
        actor_name = action.actor.username if action.actor else 'Система'
        verb = self.VERB_TRANSLATIONS.get(action.verb, action.verb)
        target_label = str(action.target) if action.target else ''
        
        if target_label:
            return f'{actor_name} {verb} "{target_label}"'
        return f'{actor_name} {verb}'
```

---

## 6. Структура Кода Headless API

### 6.1 Файловая Структура

```
mayan/apps/headless_api/
├── __init__.py
├── apps.py                     # Django AppConfig
├── urls.py                     # URL routing
├── permissions.py              # Кастомные permissions (если нужны)
├── serializers.py              # Опционально, для сложных схем
├── views/
│   ├── __init__.py
│   ├── password_views.py       # HeadlessPasswordChangeView
│   ├── config_views.py         # HeadlessDocumentTypeConfigView
│   └── activity_views.py       # HeadlessActivityFeedView
├── tests/
│   ├── __init__.py
│   ├── test_password_views.py
│   ├── test_config_views.py
│   └── test_activity_views.py
└── migrations/
    └── __init__.py
```

### 6.2 apps.py

```python
# mayan/apps/headless_api/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HeadlessApiConfig(AppConfig):
    name = 'mayan.apps.headless_api'
    verbose_name = _('Headless API')
    
    def ready(self):
        """
        Инициализация приложения.
        
        Здесь можно:
        - Регистрировать signals
        - Проверять зависимости
        - Настраивать логирование
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Headless API app initialized')
```

### 6.3 urls.py

```python
# mayan/apps/headless_api/urls.py

from django.urls import path
from .views.password_views import HeadlessPasswordChangeView
from .views.config_views import HeadlessDocumentTypeConfigView
from .views.activity_views import HeadlessActivityFeedView

app_name = 'headless_api'

urlpatterns = [
    # Password management
    path(
        'password/change/',
        HeadlessPasswordChangeView.as_view(),
        name='password-change'
    ),
    
    # Configuration exposure
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
    
    # Activity feed
    path(
        'activity/feed/',
        HeadlessActivityFeedView.as_view(),
        name='activity-feed'
    ),
]
```

### 6.4 Интеграция с Mayan URLs

```python
# mayan/urls.py (или соответствующий корневой urls.py)

from django.urls import include, path

# Добавить в urlpatterns:
urlpatterns += [
    path(
        'api/v4/headless/',
        include('mayan.apps.headless_api.urls', namespace='headless_api')
    ),
]
```

### 6.5 Регистрация в INSTALLED_APPS

```python
# mayan/settings/base.py (или конфигурация settings)

INSTALLED_APPS = [
    # ... existing apps ...
    'mayan.apps.headless_api',  # Добавить в конец
]
```

---

## 7. Интеграция с Mayan Core

### 7.1 Правила Безопасной Интеграции

1. **Используем только публичные API:**
   ```python
   # ✅ Правильно: Используем публичные модели
   from mayan.apps.documents.models import Document, DocumentType
   
   # ❌ Неправильно: Используем внутренние хелперы
   from mayan.apps.documents.utils import _internal_helper
   ```

2. **Не изменяем Mayan signals:**
   ```python
   # ✅ Правильно: Подключаем свои signals
   @receiver(post_save, sender=Document)
   def headless_log_document_create(sender, instance, created, **kwargs):
       pass
   
   # ❌ Неправильно: Модифицируем существующие
   # mayan.apps.documents.handlers.py - НЕ ТРОГАТЬ
   ```

3. **Используем Mayan permissions system:**
   ```python
   # ✅ Правильно: Используем Mayan RBAC
   from mayan.apps.permissions import Permission
   
   # Или стандартные DRF
   from rest_framework.permissions import IsAuthenticated
   ```

### 7.2 Совместимость с Mayan Updates

**Принцип:** Headless API должен выживать обновления Mayan EDMS.

**Стратегия:**
1. **Pinned imports:** Импортируем только стабильные публичные API
2. **Version checks:** Проверяем версию Mayan при startup
3. **Graceful degradation:** Если API изменилось, логируем и возвращаем error

```python
# mayan/apps/headless_api/utils.py

from django.conf import settings
import mayan

def check_mayan_compatibility():
    """Проверка совместимости с версией Mayan."""
    required_version = '4.6'
    current_version = getattr(mayan, '__version__', '0.0')
    
    if not current_version.startswith(required_version):
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f'Headless API designed for Mayan {required_version}, '
            f'current version is {current_version}. '
            'Some features may not work correctly.'
        )
```

---

## 8. Тестирование и Валидация

### 8.1 Unit Tests

```python
# mayan/apps/headless_api/tests/test_password_views.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class HeadlessPasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='oldpassword123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_password_change_success(self):
        """Успешная смена пароля."""
        response = self.client.post(
            '/api/v4/headless/password/change/',
            {
                'current_password': 'oldpassword123',
                'new_password': 'newpassword456',
                'new_password_confirm': 'newpassword456'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Проверяем, что пароль реально изменился
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))
    
    def test_password_change_wrong_current(self):
        """Неверный текущий пароль."""
        response = self.client.post(
            '/api/v4/headless/password/change/',
            {
                'current_password': 'wrongpassword',
                'new_password': 'newpassword456',
                'new_password_confirm': 'newpassword456'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'INVALID_CURRENT_PASSWORD')
    
    def test_password_change_mismatch(self):
        """Новые пароли не совпадают."""
        response = self.client.post(
            '/api/v4/headless/password/change/',
            {
                'current_password': 'oldpassword123',
                'new_password': 'newpassword456',
                'new_password_confirm': 'differentpassword'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'PASSWORD_MISMATCH')
    
    def test_password_change_unauthorized(self):
        """Без аутентификации."""
        self.client.logout()
        response = self.client.post(
            '/api/v4/headless/password/change/',
            {
                'current_password': 'oldpassword123',
                'new_password': 'newpassword456',
                'new_password_confirm': 'newpassword456'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### 8.2 Валидация после Развертывания

**Чек-лист:**

- [ ] POST `/api/v4/headless/password/change/` с валидным токеном → 200 OK
- [ ] POST `/api/v4/headless/password/change/` без токена → 401 Unauthorized
- [ ] POST `/api/v4/headless/password/change/` с неверным текущим паролем → 400 INVALID_CURRENT_PASSWORD
- [ ] GET `/api/v4/headless/config/document_types/` → Список типов с метаданными
- [ ] GET `/api/v4/headless/config/document_types/1/` → Детальная конфигурация
- [ ] GET `/api/v4/headless/activity/feed/` → Персонализированная лента
- [ ] Логирование: все операции записываются в Mayan Events

---

## 📋 Связанная Документация

- **[TRANSFORMATION_PLAN_V4.md](TRANSFORMATION_PLAN_V4.md)** — План трансформации с BFF стратегией
- **[FRONTEND_ANALYSIS_V4.md](FRONTEND_ANALYSIS_V4.md)** — План рефакторинга фронтенда
- **[TEST_EXECUTION_REPORT.md](TEST_EXECUTION_REPORT.md)** — Доказательства API сбоев

---

**Версия документа:** 4.0 (Headless API Micro-App Architecture)
**Создан:** 04 декабря 2025
**Автор:** Senior System Analyst & Backend Architect

---

*🚨 КРИТИЧЕСКИЙ ПЕРЕСМОТР: Mayan EDMS API не предоставляет необходимые self-service endpoints. Headless API Micro-App — единственный путь к production-ready SPA без модификации core Mayan.*


