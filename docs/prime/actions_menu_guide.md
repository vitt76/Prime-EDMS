# Руководство по добавлению пунктов меню в раздел "Действия" для файлов

Это руководство объясняет, как добавить новые пункты меню в раздел **"Действия"** для файлов документов в Mayan EDMS.

## 🎯 Цель

Добавить новый пункт меню со ссылкой в раздел "Действия" файлов документов (например, в `http://localhost/#/documents/documents/7/files/`).

## 📋 Предварительные требования

- Расширение должно быть уже создано и подключено
- Понимание структуры Mayan EDMS меню
- Знание Django URL patterns

## 🏗️ Структура компонентов

Для добавления пункта меню нужны:

1. **Иконка** - в `icons.py`
2. **Ссылка** - в `links/your_links.py`
3. **Регистрация** - в `apps.py`
4. **Разрешения** - опционально в `permissions.py`

## 🎨 Шаг 1: Создание иконки

### Файл: `mayan/apps/your_extension/icons.py`

```python
from mayan.apps.appearance.classes import Icon

# Иконка для вашего пункта меню
icon_your_action = Icon(
    driver_name='fontawesome',
    symbol='your-icon-name'  # Например: 'cogs', 'download', 'upload', 'share' и т.д.
)
```

### Доступные иконки FontAwesome

Популярные иконки для меню:
- `cogs` - настройки/конфигурация
- `download` - скачивание
- `upload` - загрузка
- `share` - поделиться
- `eye` - просмотр
- `edit` - редактирование
- `trash` - удаление
- `copy` - копирование
- `exchange-alt` - конвертация
- `file-alt` - файл

## 🔗 Шаг 2: Создание ссылки меню

### Файл: `mayan/apps/your_extension/links/your_links.py`

```python
from django.utils.translation import ugettext_lazy as _
from mayan.apps.navigation.classes import Link

from ..icons import icon_your_action

# Ссылка для пункта меню
link_your_action = Link(
    args='object.pk',                    # ID файла (обязательно)
    icon=icon_your_action,               # Иконка (обязательно)
    text=_('Your Action'),               # Текст меню (обязательно)
    view='your_extension:your_view',     # URL pattern (обязательно)
    permissions=('your_extension.your_permission',)  # Разрешения (опционально)
)
```

### Параметры Link

- **`args`** - аргументы для URL. Для файлов документов обычно `'object.pk'` (ID файла)
- **`icon`** - объект иконки из icons.py
- **`text`** - текст меню, обернутый в `_()` для локализации
- **`view`** - ссылка на URL pattern в формате `'namespace:view_name'`
- **`permissions`** - кортеж разрешений (опционально)
- **`tags`** - теги для стилизации (например, `tags='dangerous'` для красного цвета)

## ⚙️ Шаг 3: Регистрация в меню

### Файл: `mayan/apps/your_extension/apps.py`

```python
from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _

from .links.your_links import link_your_action

class YourExtensionApp(MayanAppConfig):
    # ... другие настройки ...

    def ready(self):
        super().ready()

        # Регистрация пункта меню для файлов документов
        self._register_file_menu_links()

    def _register_file_menu_links(self):
        """Регистрация ссылок в меню файлов документов"""
        from mayan.apps.common.menus import menu_object

        # Регистрация для модели DocumentFile
        menu_object.bind_links(
            links=(link_your_action,),      # Ваша ссылка
            sources=(DocumentFile,)         # Для каких объектов показывать
        )
```

### Важные моменты

- **`menu_object`** - глобальный объект меню для действий над объектами
- **`sources=(DocumentFile,)`** - указывает, что меню показывается для файлов документов
- Регистрация происходит в методе `ready()` приложения

## 🔒 Шаг 4: Разрешения (опционально)

### Файл: `mayan/apps/your_extension/permissions.py`

```python
from django.utils.translation import ugettext_lazy as _
from mayan.apps.permissions.classes import Permission

# Разрешение для действия
permission_your_action = Permission(
    namespace='your_extension',
    name='your_action_access',
    label=_('Can perform your action on files')
)
```

### Регистрация разрешений

```python
# В apps.py методе ready()
from mayan.apps.acls.classes import ModelPermission
from .permissions import permission_your_action

def ready(self):
    super().ready()

    # Регистрация разрешений
    ModelPermission.register(
        model=DocumentFile,  # Модель, для которой действует разрешение
        permissions=(permission_your_action,)
    )
```

## 🌐 Шаг 5: URL и представление

### Файл: `mayan/apps/your_extension/urls.py`

```python
from django.urls import path
from .views import YourActionView

app_name = 'your_extension'  # Должен совпадать с namespace в Link

urlpatterns = [
    path(
        'files/<int:document_file_id>/your-action/',
        YourActionView.as_view(),
        name='your_view'  # Должен совпадать с view в Link
    ),
]
```

### Файл: `mayan/apps/your_extension/views.py`

```python
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from mayan.apps.documents.models import DocumentFile

class YourActionView(LoginRequiredMixin, TemplateView):
    template_name = 'your_extension/your_action.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получение файла документа
        document_file = get_object_or_404(
            DocumentFile,
            pk=self.kwargs['document_file_id']
        )

        context['document_file'] = document_file
        context['document'] = document_file.document
        return context
```

## 🎨 Шаг 6: Шаблон (опционально)

### Файл: `mayan/apps/your_extension/templates/your_extension/your_action.html`

```html
{% extends "appearance/base.html" %}

{% load i18n static %}

{% block title %}{% trans "Your Action" %}{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">
                        <i class="fa fa-your-icon"></i>
                        {% trans "Your Action" %}
                    </h3>
                </div>
                <div class="panel-body">
                    <p>{% trans "Performing action on file:" %} {{ document_file }}</p>

                    <!-- Ваш контент действия -->
                    <div class="alert alert-info">
                        {% trans "Action completed successfully!" %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## 🚀 Шаг 7: Подключение расширения

### Добавление в config.yml

```yaml
common:
  extra_apps:
    - mayan.apps.your_extension
```

### Пересборка и запуск

```bash
# Пересборка Docker образа
docker build -f Dockerfile.app -t prime-edms_app:latest .

# Перезапуск системы
./ubuntu-start.sh restart
```

## ✅ Шаг 8: Проверка

1. Открыть Prime-EDMS в браузере
2. Перейти в раздел "Документы" → выбрать документ → "Файлы"
3. В меню "Действия" должен появиться новый пункт
4. При клике должна открыться ваша страница или выполниться действие

## 🔧 Расширенные возможности

### Добавление нескольких пунктов меню

```python
# links/your_links.py
link_action1 = Link(
    args='object.pk',
    icon=icon_action1,
    text=_('Action 1'),
    view='your_extension:action1'
)

link_action2 = Link(
    args='object.pk',
    icon=icon_action2,
    text=_('Action 2'),
    view='your_extension:action2'
)

# apps.py
menu_object.bind_links(
    links=(link_action1, link_action2),
    sources=(DocumentFile,)
)
```

### Условное отображение меню

```python
from mayan.apps.navigation.classes import Link

def can_perform_action(context):
    """Условие для отображения пункта меню"""
    document_file = context.get('resolved_object')
    return document_file and document_file.exists()

link_conditional_action = Link(
    args='object.pk',
    icon=icon_conditional,
    text=_('Conditional Action'),
    view='your_extension:conditional',
    conditional_disable=can_perform_action  # Условное отображение
)
```

### Добавление в другие меню

```python
# Другие типы меню
from mayan.apps.common.menus import (
    menu_list_facet,    # Фасетное меню списка
    menu_secondary,     # Вторичное меню
    menu_facet          # Основное фасетное меню
)

# Регистрация в разных меню
menu_list_facet.bind_links(links=(link_your,), sources=(DocumentFile,))
menu_secondary.bind_links(links=(link_your,), sources=(DocumentFile,))
```

## 🐛 Устранение неполадок

### Пункт меню не отображается

**Проверьте:**
- Правильность регистрации в `apps.py`
- Корректность namespace и view name
- Наличие разрешений у пользователя
- Правильность импорта ссылок

### Ссылка ведет не туда

**Проверьте:**
- Совпадение namespace в `urls.py` и `Link.view`
- Правильность URL pattern в `urls.py`
- Корректность аргументов в `Link.args`

### Ошибка доступа

**Проверьте:**
- Регистрацию разрешений в `apps.py`
- Наличие разрешений у пользователя
- Правильность указания разрешений в `Link.permissions`

## 📚 Примеры из проекта

Посмотрите на существующие реализации:

- `mayan/apps/documents/links/document_file_links.py` - базовые ссылки для файлов
- `mayan/apps/converter_pipeline_extension/` - пример расширения с меню

## 🎯 Заключение

Следуя этому руководству, вы сможете легко добавлять новые пункты меню в раздел "Действия" для файлов документов. Основные шаги:

1. Создать иконку
2. Создать ссылку с правильными параметрами
3. Зарегистрировать в menu_object
4. Создать URL и представление
5. Пересобрать и протестировать

Удачи в разработке! 🚀
