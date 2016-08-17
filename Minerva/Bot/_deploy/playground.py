import os
import pathlib

import deploy_helpers

ROOT = pathlib.Path(__file__).absolute().parent.parent.parent
print(ROOT)


dirs = []

for root, directories, filenames in os.walk(str(ROOT)):
    for d in directories:
        if not d.startswith('_'):
            dirs.append(d)

    for f in filenames:
        if f.endswith('.py') and not f.startswith('_'):
            print(os.path.join(str(ROOT), f))


for _, _, filenames in os.walk(str(dirs[0])):
    for f in filenames:
        if not f.startswith('_') and f.endswith('.py'):
            print(f)