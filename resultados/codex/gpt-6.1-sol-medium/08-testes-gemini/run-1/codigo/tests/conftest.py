"""Permite importar o módulo local também ao executar o comando pytest."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
