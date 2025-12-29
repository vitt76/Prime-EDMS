from django.db import migrations


def create_default_dam_templates(apps, schema_editor):
    NotificationTemplate = apps.get_model('notifications', 'NotificationTemplate')

    defaults = [
        {
            'event_type': 'documents.document_create',
            'title_template': 'Загружен документ: {target}',
            'message_template': '{actor} загрузил документ {target} ({timestamp})',
            'icon_type': 'success',
            'default_priority': 'NORMAL',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'primary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
        {
            'event_type': 'documents.document_file_created',
            'title_template': 'Добавлен файл в документ: {target}',
            'message_template': '{actor} добавил файл в {target} ({timestamp})',
            'icon_type': 'success',
            'default_priority': 'NORMAL',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'primary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
        {
            'event_type': 'documents.document_version_created',
            'title_template': 'Создана новая версия: {target}',
            'message_template': '{actor} создал новую версию документа {target} ({timestamp})',
            'icon_type': 'info',
            'default_priority': 'NORMAL',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'primary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
        {
            'event_type': 'documents.document_version_page_created',
            'title_template': 'Обработка страниц: {target}',
            'message_template': 'Добавлены страницы версии для {target} ({timestamp})',
            'icon_type': 'info',
            'default_priority': 'NORMAL',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'primary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
        {
            'event_type': 'documents.document_view',
            'title_template': 'Документ открыт: {target}',
            'message_template': '{actor} открыл документ {target} ({timestamp})',
            'icon_type': 'info',
            'default_priority': 'LOW',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'secondary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': False},
        },
        {
            'event_type': 'documents.document_file_downloaded',
            'title_template': 'Файл скачан: {target}',
            'message_template': '{actor} скачал файл документа {target} ({timestamp})',
            'icon_type': 'info',
            'default_priority': 'LOW',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'secondary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': False},
        },
        {
            'event_type': 'documents.document_trashed',
            'title_template': 'Документ перемещён в корзину: {target}',
            'message_template': '{actor} переместил документ в корзину: {target} ({timestamp})',
            'icon_type': 'warning',
            'default_priority': 'HIGH',
            'actions': [],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
        {
            'event_type': 'documents.trashed_document_restored',
            'title_template': 'Документ восстановлен: {target}',
            'message_template': '{actor} восстановил документ: {target} ({timestamp})',
            'icon_type': 'success',
            'default_priority': 'NORMAL',
            'actions': [
                {'id': 'view', 'label': 'Открыть', 'url': '/documents/{document_id}', 'type': 'link', 'style': 'primary'},
            ],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
        {
            'event_type': 'documents.trashed_document_deleted',
            'title_template': 'Документ удалён: {target}',
            'message_template': '{actor} удалил документ безвозвратно: {target} ({timestamp})',
            'icon_type': 'error',
            'default_priority': 'URGENT',
            'actions': [],
            'recipients_config': {'admin': True, 'editor': True, 'viewer': True},
        },
    ]

    for item in defaults:
        event_type = item['event_type']
        NotificationTemplate.objects.update_or_create(
            event_type=event_type,
            defaults={
                'title_template': item['title_template'],
                'message_template': item.get('message_template', ''),
                'icon_type': item.get('icon_type', 'info'),
                'icon_url': item.get('icon_url', ''),
                'default_priority': item.get('default_priority', 'NORMAL'),
                'actions': item.get('actions', []),
                'recipients_config': item.get('recipients_config', {}),
                'is_active': True,
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_dam_templates, migrations.RunPython.noop),
    ]


