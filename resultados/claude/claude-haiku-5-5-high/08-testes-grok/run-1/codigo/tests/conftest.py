import os
import sys

# Permite `from descontos import ...` mesmo quando o pytest roda de outro diretório.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
