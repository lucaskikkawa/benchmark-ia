import os
import sys

# Garante que o validador.py da raiz do projeto (pai de tests/) seja importável.
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
