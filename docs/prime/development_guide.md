# Полное руководство по разработке расширений

Это подробное руководство по созданию, подключению и сопровождению расширений для Prime-EDMS.

## 📋 Содержание

- [Архитектура расширений](#архитектура-расширений)
- [Создание расширения](#создание-расширения)
- [Базовые компоненты](#базовые-компоненты)
- [Расширенные возможности](#расширенные-возможности)
- [Подключение и активация](#подключение-и-активация)
- [Тестирование и отладка](#тестирование-и-отладка)
- [Развертывание](#развертывание)

## 🏗️ Архитектура расширений

Prime-EDMS использует модульную архитектуру Django приложений. Каждое расширение - это отдельное Django app со своей функциональностью.

### Структура расширения

```
mayan/apps/название_расширения/
├── __init__.py              # Объявление app config
├── apps.py                  # Конфигурация приложения
├── urls.py                  # URL маршруты
├── views.py                 # Представления (views)
├── models.py                # Модели данных
├── links/                   # Ссылки для меню
├── icons.py                 # Иконки
├── permissions.py           # Разрешения
├── locale/                  # Переводы
├── templates/               # HTML шаблоны
├── static/                  # Статические файлы
├── tests/                   # Тесты
└── migrations/              # Миграции БД
```

## 🛠️ Создание расширения

### Шаг 1: Планирование

Прежде чем создавать расширение, определите:

- **Назначение**: какую проблему решает расширение?
- **Функциональность**: какие возможности добавляет?
- **Интеграция**: где в интерфейсе будет доступна функциональность?
- **Зависимости**: какие другие расширения или системные компоненты нужны?

### Шаг 2: Создание структуры

```bash
# Использовать скрипт создания
./start_app.sh my_extension

# Или создать вручную
mkdir -p mayan/apps/my_extension
cd mayan/apps/my_extension

# Создать базовые файлы
touch __init__.py apps.py urls.py views.py models.py
mkdir -p links templates/my_extension static/my_extension/css static/my_extension/js
```

## 📝 Базовые компоненты

### 1. Конфигурация приложения (`apps.py`)

```python
from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _

class MyExtensionApp(MayanAppConfig):
    """Мое расширение для Prime-EDMS"""

    app_namespace = 'my_extension'           # Namespace для URL
    app_url = 'my-extension'                 # Префикс URL
    has_rest_api = True                      # Поддержка REST API
    has_static_media = True                  # Статические файлы
    has_tests = True                         # Модульные тесты
    name = 'mayan.apps.my_extension'         # Полное имя приложения
    verbose_name = _('My Extension')         # Отображаемое имя

    def ready(self):
        """Выполняется при загрузке приложения"""
        super().ready()
        print(f'✅ {self.verbose_name} loaded successfully!')

        # Здесь можно:
        # - Регистрировать сигналы
        # - Модифицировать другие приложения
        # - Выполнять инициализацию
```

### 2. URL маршруты (`urls.py`)

```python
from django.urls import path, include
from .views import MyView, MyAPIView

app_name = 'my_extension'  # Важно: должно совпадать с app_namespace

urlpatterns = [
    # Основные страницы
    path('', MyView.as_view(), name='main_view'),

    # REST API
    path('api/', include([
        path('items/', MyAPIView.as_view(), name='api_items'),
    ])),
]
```

### 3. Представления (`views.py`)

```python
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response

class MyView(LoginRequiredMixin, TemplateView):
    """Основное представление"""
    template_name = 'my_extension/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мое расширение'
        return context

class MyAPIView(APIView):
    """REST API представление"""

    def get(self, request):
        return Response({'message': 'Hello from API!'})
```

### 4. Модели (`models.py`)

```python
from django.db import models
from django.utils.translation import ugettext_lazy as _

class MyModel(models.Model):
    """Пример модели"""

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name')
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created')
    )

    class Meta:
        verbose_name = _('My Model')
        verbose_name_plural = _('My Models')

    def __str__(self):
        return self.name
```

## 🔗 Ссылки и меню

### Создание ссылок

```python
# links/my_links.py
from django.utils.translation import ugettext_lazy as _
from mayan.apps.navigation.classes import Link

from ..icons import icon_my_extension

link_my_extension = Link(
    icon=icon_my_extension,
    text=_('My Extension'),
    view='my_extension:main_view',
    permissions=('my_extension.view_my_model',)  # Опционально
)
```

### Регистрация в меню

```python
# В apps.py методе ready()
from mayan.apps.common.menus import menu_object
from .links.my_links import link_my_extension

def ready(self):
    super().ready()

    # Добавить ссылку в меню объектов
    menu_object.bind_links(
        links=(link_my_extension,),
        sources=(Document,)  # Для каких моделей показывать
    )
```

## 🎨 Шаблоны и статические файлы

### Структура шаблонов

```
templates/my_extension/
├── base.html          # Базовый шаблон
├── list.html          # Список объектов
├── detail.html        # Детальный просмотр
└── form.html          # Формы
```

### Пример шаблона

```html
<!-- templates/my_extension/main.html -->
{% extends "appearance/base.html" %}

{% load i18n static %}

{% block title %}{% trans "My Extension" %}{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        <i class="fa fa-cogs"></i>
                        {% trans "My Extension" %}
                    </h3>
                </div>
                <div class="panel-body">
                    <p>{% trans "Welcome to my extension!" %}</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## 🌐 Переводы (локализация)

### Создание файлов переводов

```bash
# Создать папку для переводов
mkdir -p locale/ru/LC_MESSAGES

# Создать .po файл
touch locale/ru/LC_MESSAGES/django.po
```

### Структура django.po

```po
# locale/ru/LC_MESSAGES/django.po
msgid ""
msgstr ""
"Language: ru\n"
"Content-Type: text/plain; charset=UTF-8\n"

#: views.py:10
msgid "Hello World"
msgstr "Привет Мир"

#: models.py:15
msgid "My Model"
msgstr "Моя модель"
```

### Компиляция переводов

```bash
# В контейнере
cd /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension/locale/ru/LC_MESSAGES/
msgfmt django.po -o django.mo
```

### Настройки Django для переводов

```python
# mayan/settings/base.py
LOCALE_PATHS = [
    '/opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension/locale',
]
```

## 🔒 Разрешения

### Создание разрешений

```python
# permissions.py
from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions.classes import Permission

permission_my_model_view = Permission(
    namespace='my_extension',
    name='my_model_view',
    label=_('View my model')
)

permission_my_model_edit = Permission(
    namespace='my_extension',
    name='my_model_edit',
    label=_('Edit my model')
)
```

### Регистрация разрешений

```python
# apps.py
from .permissions import permission_my_model_view, permission_my_model_edit

def ready(self):
    super().ready()

    # Регистрация разрешений
    from mayan.apps.acls.classes import ModelPermission
    ModelPermission.register(
        model=MyModel,
        permissions=(permission_my_model_view, permission_my_model_edit)
    )
```

## 🧪 Тестирование

### Структура тестов

```
tests/
├── __init__.py
├── test_models.py
├── test_views.py
├── test_api.py
└── test_permissions.py
```

### Пример теста

```python
# tests/test_views.py
from django.test import TestCase
from django.urls import reverse

class MyExtensionViewTestCase(TestCase):
    def test_main_view(self):
        """Test main view accessibility"""
        response = self.client.get(reverse('my_extension:main_view'))
        self.assertEqual(response.status_code, 200)
```

### Запуск тестов

```bash
# В контейнере
cd /opt/mayan-edms
python manage.py test my_extension
```

## 🚀 Подключение и активация

### Шаг 1: Добавление в config.yml

```yaml
common:
  extra_apps:
    - mayan.apps.my_extension
```

### Шаг 2: Копирование в Docker

```dockerfile
# Dockerfile.app
COPY mayan/apps/my_extension /opt/mayan-edms/lib/python3.9/site-packages/mayan/apps/my_extension
```

### Шаг 3: Сборка и запуск

```bash
# Пересборка образа
docker build -f Dockerfile.app -t prime-edms_app:latest .

# Перезапуск системы
./ubuntu-start.sh restart
```

### Шаг 4: Миграции (если есть модели)

```bash
# В контейнере
python manage.py makemigrations my_extension
python manage.py migrate my_extension
```

## 🔧 Расширенные возможности

### Сигналы Django

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MyModel

@receiver(post_save, sender=MyModel)
def my_model_saved(sender, instance, **kwargs):
    """Обработчик сигнала сохранения модели"""
    print(f'MyModel {instance} was saved!')
```

### Фоновые задачи (Celery)

```python
# tasks.py
from celery import shared_task

@shared_task
def my_background_task(data):
    """Фоновая задача"""
    # Обработка данных
    return f'Processed: {data}'
```

### REST API

```python
# serializers.py
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = '__all__'

# views.py
from rest_framework import viewsets
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

### Кастомные команды

```python
# management/commands/my_command.py
from django.core.management.base import BaseCommand
from ...models import MyModel

class Command(BaseCommand):
    help = 'My custom command'

    def handle(self, *args, **options):
        self.stdout.write('Running my command...')
        # Логика команды
```

## 📦 Развертывание

### Производственная среда

1. **Тестирование**: убедитесь, что все тесты проходят
2. **Документация**: обновите документацию расширения
3. **Миграции**: создайте и примените миграции БД
4. **Зависимости**: проверьте системные зависимости
5. **Мониторинг**: добавьте логирование и метрики

### Автоматизация развертывания

```bash
#!/bin/bash
# deploy_extension.sh

EXTENSION_NAME=$1

# Проверка наличия расширения
if [ ! -d "mayan/apps/$EXTENSION_NAME" ]; then
    echo "Extension $EXTENSION_NAME not found!"
    exit 1
fi

# Добавление в config.yml
echo "  - mayan.apps.$EXTENSION_NAME" >> config.yml

# Пересборка и перезапуск
make restart

echo "Extension $EXTENSION_NAME deployed successfully!"
```

## 🐛 Устранение неполадок

См. [руководство по устранению неполадок](troubleshooting.md)

## 📚 Дополнительные ресурсы

- [Django documentation](https://docs.djangoproject.com/)
- [Mayan EDMS API](https://docs.mayan-edms.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery documentation](https://docs.celeryproject.org/)
