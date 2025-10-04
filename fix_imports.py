import os
import re

for root, dirs, files in os.walk('scripts'):
    for file in files:
        if not file.endswith('.py'):
            continue
        filepath = os.path.join(root, file)
        with open(filepath, 'r') as f:
            content = f.read()

        original = content
        # Check if file uses Optional or Union
        uses_optional = 'Optional[' in content
        uses_union = 'Union[' in content

        if not (uses_optional or uses_union):
            continue

        # Check if typing import exists
        if 'from typing import' in content:
            # Get the first typing import line
            match = re.search(r'from typing import ([^\n]+)', content)
            if match:
                imports = match.group(1)
                needs_optional = uses_optional and 'Optional' not in imports
                needs_union = uses_union and 'Union' not in imports

                if needs_optional or needs_union:
                    new_imports = imports
                    if needs_optional:
                        new_imports += ', Optional'
                    if needs_union:
                        new_imports += ', Union'
                    content = content.replace(f'from typing import {imports}', f'from typing import {new_imports}', 1)
        else:
            # Add new import
            imports_needed = []
            if uses_optional:
                imports_needed.append('Optional')
            if uses_union:
                imports_needed.append('Union')

            if imports_needed:
                # Find first import line
                first_import = re.search(r'^(import |from )', content, re.MULTILINE)
                if first_import:
                    pos = first_import.start()
                    content = content[:pos] + f"from typing import {', '.join(imports_needed)}\n\n" + content[pos:]

        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f'Fixed: {filepath}')

print('Done!')
