import os
import pathlib

ROOT = pathlib.Path(__file__).absolute().parent.parent.parent
print(ROOT)

print(os.listdir(str(ROOT)))

for _, _, filenames in os.walk(str(ROOT)):
    for f in filenames:
        print(os.path.join(str(ROOT), f))