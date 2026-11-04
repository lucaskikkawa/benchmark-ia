"""Permite importar o módulo ao executar tanto pytest quanto python -m pytest."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
