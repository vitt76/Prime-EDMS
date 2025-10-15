from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .literals import DJANGO_SQLITE_BACKEND


def check_for_sqlite():
    return settings.DATABASES['default']['ENGINE'] == DJANGO_SQLITE_BACKEND and settings.DEBUG is False


def check_queryset(self, queryset):
    """
    Validate that a view queryset is usable.
    """
    try:
        queryset.query
    except AttributeError:
        # Check if it is an iterable.
        try:
            iter(queryset)
        except TypeError as exception:
            raise ImproperlyConfigured(
                'Queryset `{}` of view `{}` is not a valid queryset.'.format(
                    queryset, self.__class__
                )
            ) from exception
        else:
            return queryset
    else:
        return queryset


def instance_list_to_queryset(instance_list):
    manager = instance_list[0]._meta.default_manager

    return manager.filter(pk__in=[instance.pk for instance in instance_list])
