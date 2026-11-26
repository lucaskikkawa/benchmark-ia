from pathlib import Path
import sys

ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.append(ROOT)
