import os
import sys
from pathlib import Path

_parent = str(Path(__file__).resolve().parent.parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)
_cwd = os.getcwd()
if _cwd not in sys.path:
    sys.path.insert(0, _cwd)
