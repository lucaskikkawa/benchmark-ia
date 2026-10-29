import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
caminho = str(RAIZ)
if caminho not in sys.path:
    sys.path.insert(0, caminho)
