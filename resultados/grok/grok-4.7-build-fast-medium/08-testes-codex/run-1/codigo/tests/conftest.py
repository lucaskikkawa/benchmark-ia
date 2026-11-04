import sys
from pathlib import Path

# A suíte importa o módulo ao lado de tests/, qualquer que seja o cwd.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
