import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
raiz = str(Path(__file__).resolve().parent.parent)
if raiz not in sys.path:
    sys.path.insert(0, raiz)
