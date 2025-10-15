from django.apps import apps
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mayan.apps.templating.classes import Template

from .classes import EventType
from .literals import TEXT_UNKNOWN_EVENT_ID


def widget_event_actor_link(context, attribute=None):
    entry = context['object']

    ContentType = apps.get_model(
        app_label='contenttypes', model_name='ContentType'
    )

    if attribute:
        entry = getattr(entry, attribute)

    if entry.actor == entry.target:
        label = _('System')
        url = None
    else:
        label = entry.actor
        content_type = ContentType.objects.get_for_model(model=entry.actor)

        url = reverse(
            viewname='events:object_event_list', kwargs={
                'app_label': content_type.app_label,
                'model_name': content_type.model,
                'object_id': entry.actor.pk
            }
        )

    if url:
        return Template(
            template_string='<a href="{{ url }}">{{ label }}</a>'
        ).render(context={'label': entry.actor, 'url': url})
    else:
        return label


def widget_event_type_link(context, attribute=None):
    entry = context['object']

    if attribute:
        entry = getattr(entry, attribute)

    try:
        event_type_label = EventType.get(id=entry.verb).label
    except KeyError:
        event_type_label = TEXT_UNKNOWN_EVENT_ID % entry.verb

    return mark_safe(
        '<a href="{url}">{label}</a>'.format(
            url=reverse(
                viewname='events:verb_event_list', kwargs={'verb': entry.verb}
            ), label=event_type_label
        )
    )
