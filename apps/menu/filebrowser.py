import inspect
import os
import importlib.util
from pathlib import Path

full_path = os.path.dirname(os.path.abspath(__file__))
rootpath = (str(Path(full_path).parents[1]))

print(rootpath)
