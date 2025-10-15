import json
import os

from django import forms as django_forms
from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import (
    get_fields_from_path, help_text_for_field, label_for_field
)
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db import models
from django.db.models import Model
from django.db.models.query import QuerySet
from django.forms import Form as DjangoForm, ModelForm as DjangoModelForm
from django.forms.models import ModelFormMetaclass
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.utils import resolve_attribute

from .widgets import DisableableSelectWidget, PlainWidget, TextAreaDiv


class FormFieldsetMixin:
    fieldsets = None

    def get_fieldsets(self):
        if self.fieldsets:
            return self.fieldsets
        else:
            return (
                (
                    None, {
                        'fields': tuple(self.fields)
                    }
                ),
            )


class Form(FormFieldsetMixin, DjangoForm):
    """Mayan's default form class."""


class ModelForm(FormFieldsetMixin, DjangoModelForm):
    """Mayan's default model form class."""


class ChoiceForm(Form):
    """
    Form to be used in side by side templates used to add or remove
    items from a many to many field.
    """
    search = django_forms.CharField(
        label=_('Search'), required=False, widget=django_forms.widgets.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'views-select-search',
                'placeholder': 'Filter list'
            }
        )
    )
    selection = django_forms.MultipleChoiceField(
        required=False, widget=DisableableSelectWidget()
    )

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        label = kwargs.pop('label', _('Selection'))
        help_text = kwargs.pop('help_text', None)
        disabled_choices = kwargs.pop('disabled_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['selection'].choices = choices
        self.fields['selection'].label = label
        self.fields['selection'].help_text = help_text
        self.fields['selection'].widget.disabled_choices = disabled_choices
        self.fields['selection'].widget.attrs.update(
            {
                'class': 'full-height input-hotkey-double-click',
                'data-height-difference': '495'
            }
        )


class FormOptions:
    def __init__(self, form, kwargs, options=None):
        """
        Option definitions will be iterated. The option value will be
        determined in the following order: as passed via keyword
        arguments during form intialization, as form get_... method or
        finally as static Meta options. This is to allow a form with
        Meta options or method to be overridden at initialization
        and increase the usability of a single class.
        """
        for name, default_value in self.option_definitions.items():
            try:
                # Check for a runtime value via kwargs
                value = kwargs.pop(name)
            except KeyError:
                try:
                    # Check if there is a get_... method
                    value = getattr(self, 'get_{}'.format(name))()
                except AttributeError:
                    try:
                        # Check the meta class options
                        value = getattr(options, name)
                    except AttributeError:
                        value = default_value

            setattr(self, name, value)


class DetailFormOption(FormOptions):
    # Dictionary list of option names and default values.
    option_definitions = {'extra_fields': []}


class DetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.opts = DetailFormOption(
            form=self, kwargs=kwargs, options=getattr(self, 'Meta', None)
        )
        super().__init__(*args, **kwargs)

        for field_index, extra_field in enumerate(iterable=self.opts.extra_fields):
            obj = extra_field.get('object', self.instance)
            field = extra_field.get('field', None)
            func = extra_field.get('func', None)
            label = extra_field.get('label', None)
            help_text = extra_field.get('help_text', None)

            if field:
                if not label:
                    # If label is not specified try to get it from the object
                    # itself.
                    try:
                        fields = get_fields_from_path(model=obj, path=field)
                    except FieldDoesNotExist:
                        # Might be property of a method.
                        label = getattr(
                            getattr(obj, field), 'short_description',
                            field
                        )
                    else:
                        label = label_for_field(
                            model=obj, name=fields[-1].name
                        )

                if not help_text:
                    # If help_text is not specified try to get it from the
                    # object itself.
                    try:
                        fields = get_fields_from_path(model=obj, path=field)
                    except FieldDoesNotExist:
                        # Might be property of a method.
                        help_text = getattr(
                            getattr(obj, field), 'help_text', None
                        )
                    else:
                        help_text = help_text_for_field(
                            model=obj, name=fields[-1].name
                        )

                value = resolve_attribute(attribute=field, obj=obj)

            if func:
                value = func(obj)

            field = field or 'anonymous_field_{}'.format(field_index)

            if isinstance(value, models.query.QuerySet):
                self.fields[field] = django_forms.ModelMultipleChoiceField(
                    queryset=value, label=label
                )
            else:
                self.fields[field] = django_forms.CharField(
                    initial=value, label=label, help_text=help_text,
                    widget=extra_field.get('widget', PlainWidget)
                )

        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs.update(
                {'readonly': 'readonly'}
            )


class DynamicFormMixin:
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema')
        super().__init__(*args, **kwargs)

        widgets = self.schema.get('widgets', {})
        field_order = self.schema.get(
            'field_order', self.schema['fields'].keys()
        )

        for field_name in field_order:
            field_data = self.schema['fields'][field_name]
            field_class = import_string(dotted_path=field_data['class'])
            kwargs = {
                'label': field_data['label'],
                'required': field_data.get('required', True),
                'initial': field_data.get('default', None),
                'help_text': field_data.get('help_text'),
            }
            if widgets and field_name in widgets:
                widget = widgets[field_name]
                kwargs['widget'] = import_string(
                    dotted_path=widget['class']
                )(**widget.get('kwargs', {}))

            kwargs.update(field_data.get('kwargs', {}))
            self.fields[field_name] = field_class(**kwargs)

    @property
    def media(self):
        """
        Append the media of the dynamic fields to the normal fields' media.
        """
        media = super().media
        media = media + django_forms.Media(**self.schema.get('media', {}))
        return media


class DynamicForm(DynamicFormMixin, Form):
    """Normal dynamic form."""


class DynamicModelForm(DynamicFormMixin, ModelForm):
    """Dynamic model form."""


class DynamicFormMetaclass(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super(DynamicFormMetaclass, mcs).__new__(
            mcs=mcs, name=name, bases=bases, attrs=attrs
        )

        if new_class._meta.fields:
            new_class._meta.fields += ('backend_data',)
            widgets = getattr(new_class._meta, 'widgets', {}) or {}
            widgets['backend_data'] = django_forms.widgets.HiddenInput
            new_class._meta.widgets = widgets

        return new_class


class BackendDynamicForm(DynamicModelForm, metaclass=DynamicFormMetaclass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        backend_data = self.instance.get_backend_data()

        if backend_data:
            for field_name in self.instance.get_backend().get_fields():
                self.fields[field_name].initial = backend_data.get(
                    field_name, None
                )

    def clean(self):
        data = super().clean()

        # Consolidate the dynamic fields into a single JSON field called
        # 'backend_data'.
        backend_data = {}

        for field_name, field_data in self.schema['fields'].items():
            backend_data[field_name] = data.pop(
                field_name, field_data.get('default', None)
            )
            if isinstance(backend_data[field_name], QuerySet):
                # Flatten the queryset to a list of ids.
                backend_data[field_name] = list(
                    backend_data[field_name].values_list('id', flat=True)
                )
            elif isinstance(backend_data[field_name], Model):
                # Store only the ID of a model instance.
                backend_data[field_name] = backend_data[field_name].pk

        data['backend_data'] = json.dumps(obj=backend_data)

        return data


class FileDisplayForm(Form):
    DIRECTORY = None
    FILENAME = None

    text = django_forms.CharField(
        label='',
        widget=TextAreaDiv(
            attrs={
                'class': 'full-height scrollable',
                'data-height-difference': 270
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.DIRECTORY or self.FILENAME:
            file_path = os.path.join(
                settings.BASE_DIR, os.sep.join(self.DIRECTORY), self.FILENAME
            )
            with open(file=file_path) as file_object:
                self.fields['text'].initial = file_object.read()


class FilteredSelectionFormOptions(FormOptions):
    # Dictionary list of option names and default values.
    option_definitions = {
        'allow_multiple': False,
        'field_name': None,
        'help_text': None,
        'label': None,
        'model': None,
        'permission': None,
        'queryset': None,
        'required': True,
        'user': None,
        'widget_class': None,
        'widget_attributes': {'size': '10'},
    }


class FilteredSelectionForm(Form):
    """
    Form to select the from a list of choice filtered by access. Can be
    configure to allow single or multiple selection.
    """
    def __init__(self, *args, **kwargs):
        opts = FilteredSelectionFormOptions(
            form=self, kwargs=kwargs, options=getattr(self, 'Meta', None)
        )

        if opts.queryset is None:
            if not opts.model:
                raise ImproperlyConfigured(
                    '{} requires a queryset or a model to be specified as '
                    'a meta option or passed during initialization.'.format(
                        self.__class__.__name__
                    )
                )

            queryset = opts.model.objects.all()
        else:
            queryset = opts.queryset

        if opts.allow_multiple:
            extra_kwargs = {}
            field_class = django_forms.ModelMultipleChoiceField
            widget_class = django_forms.widgets.SelectMultiple
        else:
            extra_kwargs = {'empty_label': None}
            field_class = django_forms.ModelChoiceField
            widget_class = django_forms.widgets.Select

        if opts.widget_class:
            widget_class = opts.widget_class

        if opts.permission:
            AccessControlList = apps.get_model(
                app_label='acls', model_name='AccessControlList'
            )
            queryset = AccessControlList.objects.restrict_queryset(
                permission=opts.permission, queryset=queryset,
                user=opts.user
            )

        super().__init__(*args, **kwargs)

        self.fields[opts.field_name] = field_class(
            help_text=opts.help_text, label=opts.label,
            queryset=queryset, required=opts.required,
            widget=widget_class(attrs=opts.widget_attributes),
            **extra_kwargs
        )


class RelationshipForm(Form):
    def __init__(self, *args, **kwargs):
        self._event_actor = kwargs.pop('_event_actor')
        super().__init__(*args, **kwargs)

        self.fields['label'] = django_forms.CharField(
            label=_('Label'), required=False,
            widget=django_forms.TextInput(attrs={'readonly': 'readonly'})
        )
        self.fields['relationship_type'] = django_forms.ChoiceField(
            label=_('Relationship'),
            widget=django_forms.RadioSelect(), choices=self.RELATIONSHIP_CHOICES
        )

        self.sub_object = self.initial.get('sub_object')
        if self.sub_object:
            self.fields['label'].initial = str(self.sub_object)

            self.initial_relationship_type = self.get_relationship_type()

            self.fields['relationship_type'].initial = self.initial_relationship_type

    def get_new_relationship_instance(self):
        related_manager = getattr(
            self.initial.get('object'),
            self.initial['relationship_related_field']
        )
        main_field_name = related_manager.field.name

        return related_manager.model(
            **{
                main_field_name: self.initial.get('object'),
                self.initial['relationship_related_query_field']: self.initial.get('sub_object')
            }
        )

    def get_relationship_queryset(self):
        return getattr(
            self.initial.get('object'),
            self.initial['relationship_related_field']
        ).filter(
            **{
                self.initial['relationship_related_query_field']: self.initial.get('sub_object')
            }
        )

    def get_relationship_instance(self):
        relationship_queryset = self.get_relationship_queryset()
        if relationship_queryset.exists():
            return relationship_queryset.get()
        else:
            return self.get_new_relationship_instance()

    def save(self):
        if self.sub_object:
            if self.cleaned_data['relationship_type'] != self.initial_relationship_type:
                save_method = getattr(
                    self, 'save_relationship_{}'.format(
                        self.cleaned_data['relationship_type']
                    )
                )
                save_method()
