"""Management command to export OpenAPI schema to openapi.yaml."""

import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from drf_spectacular.generators import SchemaGenerator


class Command(BaseCommand):
    help = 'Export OpenAPI schema to a YAML or JSON file (default: docs/api/openapi.yaml).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o',
            default='docs/api/openapi.yaml',
            help='Output file path (default: docs/api/openapi.yaml)',
        )
        parser.add_argument(
            '--format',
            choices=('yaml', 'json'),
            default='yaml',
            help='Output format (default: yaml)',
        )

    def handle(self, *args, **options):
        output_path = options['output']
        output_format = options['format']

        generator = SchemaGenerator()
        schema = generator.get_schema()
        # Apply postprocessing hooks (e.g. X-Organization-Id header)
        for hook_path in settings.SPECTACULAR_SETTINGS.get('POSTPROCESSING_HOOKS', []):
            from django.utils.module_loading import import_string
            hook = import_string(hook_path)
            schema = hook(schema, generator)

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            if output_format == 'json':
                json.dump(schema, f, indent=2, ensure_ascii=False)
            else:
                try:
                    import yaml
                    yaml.dump(
                        schema,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )
                except ImportError:
                    self.stderr.write(
                        'PyYAML not available; writing JSON instead. '
                        'Install PyYAML or use --format json.'
                    )
                    f.seek(0)
                    f.truncate()
                    json.dump(schema, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS('Schema written to %s' % output_path))
