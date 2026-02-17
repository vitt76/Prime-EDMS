"""OpenAPI schema hooks for drf-spectacular.

Adds global X-Organization-Id header to all operations for multi-tenant API docs.
"""


def postprocess_schema_add_x_organization_id(result, generator, **kwargs):
    """Add X-Organization-Id header parameter to every operation."""
    x_org_param = {
        'name': 'X-Organization-Id',
        'in': 'header',
        'required': False,
        'description': (
            'Organization context for multi-tenant requests. '
            'Only applied if the authenticated user is a member of the given organization.'
        ),
        'schema': {
            'type': 'string',
            'format': 'uuid',
        },
    }
    paths = result.get('paths', {})
    for path, path_item in paths.items():
        for method in ('get', 'post', 'put', 'patch', 'delete', 'head', 'options'):
            op = path_item.get(method)
            if not op:
                continue
            params = op.get('parameters') or []
            if not any(p.get('name') == 'X-Organization-Id' for p in params):
                op['parameters'] = params + [x_org_param.copy()]
    return result
