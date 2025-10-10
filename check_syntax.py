import ast
with open('mayan/apps/converter_pipeline_extension/views.py', 'r') as f:
    content = f.read()
try:
    ast.parse(content)
    print('Syntax is valid')
except SyntaxError as e:
    print(f'Syntax error: {e}')
    print(f'Line {e.lineno}: {content.splitlines()[e.lineno-1] if e.lineno <= len(content.splitlines()) else "N/A"}')
