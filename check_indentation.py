with open('mayan/apps/converter_pipeline_extension/views.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[810:825], 811):
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        content = '' if line.strip() else '(empty)'
        print(f'{i:3}: {indent_str}{content} | {repr(line.rstrip())}')
