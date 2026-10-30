import os
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
for _p in (_AQUI, os.path.dirname(_AQUI)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
