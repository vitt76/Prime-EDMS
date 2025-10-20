# Устранение неполадок при разработке расширений

Это руководство поможет решить типичные проблемы при создании и подключении расширений для Prime-EDMS.

## 🔍 Диагностика проблем

### Проверка статуса расширения

```bash
# Проверить логи загрузки
docker logs prime-edms_app_1 | grep -i "extension\|app"

# Проверить, что расширение в списке установленных
docker exec prime-edms_app_1 python3 -c "
import django
django.setup()
from django.apps import apps
extensions = [app.name for app in apps.get_app_configs() if 'mayan.apps.' in app.name]
print('Installed extensions:', extensions)
"
```

### Проверка конфигурации

```bash
# Проверить config.yml
cat config.yml

# Проверить, что расширение скопировано в контейнер
docker exec prime-edms_app_1 ls -la /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension/
```

## 🐛 Распространенные проблемы

### 1. Расширение не загружается

**Симптомы:**
- Расширение не отображается в меню
- Логи содержат ошибки импорта

**Возможные причины:**
- Неправильный путь в `config.yml`
- Ошибки в `__init__.py` или `apps.py`
- Отсутствие обязательных файлов

**Решения:**

```yaml
# config.yml - правильный формат
common:
  extra_apps:
    - mayan.apps.my_extension
```

```python
# __init__.py - правильное объявление
default_app_config = 'mayan.apps.my_extension.apps.MyExtensionApp'
```

```python
# apps.py - правильное наследование
from mayan.apps.common.apps import MayanAppConfig

class MyExtensionApp(MayanAppConfig):
    name = 'mayan.apps.my_extension'  # Должен совпадать с путем
```

### 2. Меню не отображается

**Симптомы:**
- Расширение загружается, но пункты меню отсутствуют

**Возможные причины:**
- Неправильный namespace в ссылках
- Отсутствие регистрации в меню
- Проблемы с разрешениями

**Решения:**

```python
# links/my_links.py - правильный namespace
link_my_feature = Link(
    view='my_extension:my_view',  # namespace:view_name
    # ...
)
```

```python
# apps.py - регистрация в меню
from mayan.apps.common.menus import menu_object
from .links.my_links import link_my_feature

def ready(self):
    super().ready()
    menu_object.bind_links(
        links=(link_my_feature,),
        sources=(Document,),  # Указать модель-источник
    )
```

### 3. URL не разрешаются (404 ошибки)

**Симптомы:**
- Ссылка ведет на неправильный URL или 404

**Возможные причины:**
- Неправильный namespace в `apps.py`
- Несоответствие между `app_namespace` и `app_name` в urls.py
- Конфликт URL с другими расширениями

**Решения:**

```python
# apps.py - правильные namespace
class MyExtensionApp(MayanAppConfig):
    app_namespace = 'my_extension'  # Должен совпадать с app_name в urls.py
    app_url = 'my-extension'        # Префикс URL
```

```python
# urls.py - правильный app_name
app_name = 'my_extension'  # Должен совпадать с app_namespace
```

### 4. Переводы не работают

**Симптомы:**
- Текст отображается на английском вместо русского

**Возможные причины:**
- Не настроены `LOCALE_PATHS`
- Не скомпилированы `.mo` файлы
- Неправильная структура файлов переводов

**Решения:**

```python
# settings/base.py - добавить LOCALE_PATHS
LOCALE_PATHS = [
    '/opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension/locale',
]
```

```bash
# Компиляция переводов
cd /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension/locale/ru/LC_MESSAGES/
msgfmt django.po -o django.mo
```

```
# Правильная структура файлов переводов
locale/
└── ru/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo  # Должен быть скомпилирован
```

### 5. Проблемы с Docker сборкой

**Симптомы:**
- Сборка образа завершается с ошибкой
- Изменения не применяются

**Возможные причины:**
- Синтаксические ошибки в коде
- Неправильные пути в Dockerfile
- Конфликты зависимостей

**Решения:**

```dockerfile
# Dockerfile.app - правильное копирование
COPY mayan/apps/my_extension /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension
COPY mayan/settings/base.py /opt/mayan-edms/lib/python3.9/site-packages/mayan/settings/base.py
```

```bash
# Очистка кэша Docker
docker system prune -f
docker volume prune -f

# Пересборка без кэша
docker build --no-cache -f Dockerfile.app -t prime-edms_app:latest .
```

### 6. Ошибки миграций БД

**Симптомы:**
- Ошибки при запуске после добавления моделей

**Возможные причины:**
- Не созданы миграции
- Конфликты с существующими миграциями

**Решения:**

```bash
# Создание миграций
docker exec prime-edms_app_1 python manage.py makemigrations my_extension

# Применение миграций
docker exec prime-edms_app_1 python manage.py migrate my_extension

# Просмотр SQL миграций
docker exec prime-edms_app_1 python manage.py sqlmigrate my_extension 0001
```

### 7. Проблемы с разрешениями

**Симптомы:**
- Доступ запрещен к функциям расширения

**Возможные причины:**
- Не зарегистрированы разрешения
- Не настроены роли пользователей

**Решения:**

```python
# permissions.py
from mayan.apps.permissions.classes import Permission

permission_my_feature = Permission(
    namespace='my_extension',
    name='my_feature_access',
    label='Access my feature'
)
```

```python
# apps.py
from mayan.apps.acls.classes import ModelPermission
from .permissions import permission_my_feature

def ready(self):
    super().ready()
    ModelPermission.register(
        model=MyModel,
        permissions=(permission_my_feature,)
    )
```

### 8. Проблемы с REST API

**Симптомы:**
- API endpoints не доступны или возвращают ошибки

**Возможные причины:**
- Не включен REST API в apps.py
- Неправильная настройка сериализаторов
- Конфликты URL

**Решения:**

```python
# apps.py
class MyExtensionApp(MayanAppConfig):
    has_rest_api = True  # Включить REST API
```

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .viewsets import MyViewSet

router = DefaultRouter()
router.register(r'my-models', MyViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## 🔧 Инструменты диагностики

### Отладочный скрипт для проверки расширения

```python
#!/usr/bin/env python3
# debug_extension.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings')
import django
django.setup()

from django.apps import apps
from django.urls import reverse, resolve
from django.conf import settings

def check_extension(extension_name):
    print(f"=== Checking extension: {extension_name} ===")

    # Check if app is installed
    try:
        app = apps.get_app_config(extension_name.split('.')[-1])
        print(f"✅ App found: {app.verbose_name}")
    except:
        print("❌ App not found")
        return

    # Check URLs
    try:
        app_urls = [url for url in settings.ROOT_URLCONF if extension_name in str(url)]
        print(f"✅ URL patterns: {len(app_urls)} found")
    except:
        print("❌ URL check failed")

    # Check models
    models = [model for model in app.get_models()]
    print(f"📊 Models: {len(models)}")

    print("✅ Extension check completed\n")

if __name__ == '__main__':
    check_extension('mayan.apps.my_extension')
```

### Проверка логов в реальном времени

```bash
# Мониторинг логов
docker logs -f prime-edms_app_1

# Поиск ошибок
docker logs prime-edms_app_1 | grep -i error

# Проверка загрузки расширений
docker logs prime-edms_app_1 | grep -A5 -B5 "extension"
```

## 🚀 Профилактика проблем

### Лучшие практики разработки

1. **Тестируйте инкрементально**
   - Добавляйте по одной функции за раз
   - Тестируйте после каждого изменения

2. **Используйте отладку**
   - Добавляйте print statements в ready()
   - Проверяйте логи после каждого перезапуска

3. **Следуйте конвенциям**
   - Используйте правильные namespace
   - Следуйте структуре существующих расширений

4. **Документируйте изменения**
   - Ведите changelog для расширения
   - Документируйте API и настройки

### Автоматизация проверки

```bash
#!/bin/bash
# check_extension.sh

EXTENSION_NAME=$1

echo "=== Checking extension: $EXTENSION_NAME ==="

# Check if directory exists
if [ ! -d "mayan/apps/$EXTENSION_NAME" ]; then
    echo "❌ Extension directory not found"
    exit 1
fi

# Check required files
required_files="__init__.py apps.py urls.py views.py"
for file in $required_files; do
    if [ ! -f "mayan/apps/$EXTENSION_NAME/$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

# Check config.yml
if ! grep -q "$EXTENSION_NAME" config.yml; then
    echo "❌ Extension not in config.yml"
    exit 1
fi

echo "✅ Extension structure OK"
echo "Ready for deployment!"
```

## 📞 Получение помощи

### Источники информации

1. **Логи приложения**
   ```bash
   docker logs prime-edms_app_1
   ```

2. **Документация Mayan EDMS**
   - https://docs.mayan-edms.com/
   - API reference и примеры

3. **Исходный код существующих расширений**
   - `mayan/apps/converter_pipeline_extension/`
   - Другие встроенные приложения Mayan

4. **Django документация**
   - https://docs.djangoproject.com/
   - Руководства по приложениям и URL

### Когда обращаться за помощью

- Проверили все пункты из этого руководства
- Изучены логи и сообщения об ошибках
- Протестировали на чистой установке
- Проблема воспроизводится последовательно

### Контакты

- Создайте issue в репозитории проекта
- Опишите проблему с полной информацией:
  - Версия Prime-EDMS
  - Шаги для воспроизведения
  - Логи ошибок
  - Конфигурация системы
