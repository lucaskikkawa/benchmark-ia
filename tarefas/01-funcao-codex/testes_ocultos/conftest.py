from pathlib import Path
import sys

# A solução é importada do diretório de trabalho montado pelo runner.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
