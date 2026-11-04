import os
import sys

# Permite `from descontos import ...` independentemente do diretório de execução do pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
