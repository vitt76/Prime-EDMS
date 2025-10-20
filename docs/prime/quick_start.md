# Быстрый старт: создание и подключение расширения

Это руководство поможет быстро создать и подключить новое расширение для Prime-EDMS.

## 🎯 Цель

Создать расширение "Hello World", которое добавляет пункт меню и страницу с приветствием.

## 📁 Шаг 1: Создание структуры расширения

### Вариант 1: Использование скрипта (рекомендуется)

```bash
# Создать расширение с базовой структурой
./start_app.sh hello_world

# Или вручную создать папку
mkdir -p mayan/apps/hello_world
```

### Вариант 2: Ручное создание

```bash
# Создать папку расширения
mkdir -p mayan/apps/hello_world

# Создать обязательные файлы
touch mayan/apps/hello_world/__init__.py
touch mayan/apps/hello_world/apps.py
touch mayan/apps/hello_world/urls.py
touch mayan/apps/hello_world/views.py
touch mayan/apps/hello_world/models.py
```

## 📝 Шаг 2: Реализация базовых файлов

### `mayan/apps/hello_world/__init__.py`
```python
default_app_config = 'mayan.apps.hello_world.apps.HelloWorldApp'
```

### `mayan/apps/hello_world/apps.py`
```python
from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _

class HelloWorldApp(MayanAppConfig):
    app_namespace = 'hello_world'
    app_url = 'hello-world'
    has_rest_api = False
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.hello_world'
    verbose_name = _('Hello World Extension')

    def ready(self):
        super().ready()
        print('🌟 Hello World extension loaded!')
```

### `mayan/apps/hello_world/urls.py`
```python
from django.urls import path
from .views import HelloWorldView

app_name = 'hello_world'

urlpatterns = [
    path('', HelloWorldView.as_view(), name='hello_world'),
]
```

### `mayan/apps/hello_world/views.py`
```python
from django.views.generic import TemplateView

class HelloWorldView(TemplateView):
    template_name = 'hello_world/hello.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'Hello from Prime-EDMS extension!'
        return context
```

## 🎨 Шаг 3: Создание шаблона

```bash
# Создать папку для шаблонов
mkdir -p mayan/apps/hello_world/templates/hello_world

# Создать шаблон
cat > mayan/apps/hello_world/templates/hello_world/hello.html << 'EOF'
{% extends "appearance/base.html" %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">🌟 Hello World Extension</h3>
                </div>
                <div class="panel-body">
                    <p class="lead">{{ message }}</p>
                    <p>Это ваше первое расширение для Prime-EDMS!</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
```

## 🔗 Шаг 4: Добавление в меню

### Создать файл ссылок
```bash
mkdir -p mayan/apps/hello_world/links
```

### `mayan/apps/hello_world/links/__init__.py`
```python
# Пустой файл
```

### `mayan/apps/hello_world/links/hello_links.py`
```python
from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

link_hello_world = Link(
    icon='fa-smile-o',
    text=_('Hello World'),
    view='hello_world:hello_world'
)
```

### Добавить ссылку в меню в `mayan/apps/documents/apps.py`
```python
# В методе ready() добавить:
from mayan.apps.hello_world.links.hello_links import link_hello_world

# Найти секцию menu_object.bind_links и добавить:
menu_object.bind_links(
    links=(
        link_hello_world,  # Добавить эту строку
        link_cache_partition_purge,
        # ... остальные ссылки
    ),
    sources=(Document,)
)
```

## ⚙️ Шаг 5: Подключение расширения

### Добавить в `config.yml`
```yaml
common:
  extra_apps:
    - mayan.apps.hello_world
```

## 🐳 Шаг 6: Сборка и запуск

```bash
# Пересобрать Docker образ
docker build -f Dockerfile.app -t prime-edms_app:latest .

# Перезапустить систему
./ubuntu-start.sh restart
```

## ✅ Шаг 7: Проверка

1. Открыть Prime-EDMS в браузере
2. Перейти в раздел "Документы"
3. В меню "Действия" должен появиться пункт "Hello World"
4. При клике должна открыться страница с приветствием

## 🎉 Поздравляем!

Вы создали первое расширение для Prime-EDMS! Теперь можете:

- Изучить [полное руководство](development_guide.md) для продвинутых возможностей
- Добавить новые функции в свое расширение
- Создать собственные расширения по аналогии

## 🐛 Возникли проблемы?

Смотрите [устранение неполадок](troubleshooting.md) или проверьте логи:

```bash
docker logs prime-edms_app_1
```
