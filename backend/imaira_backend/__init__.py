import sys
from pathlib import Path

# Extend package search path so imaira_backend and backend are unified
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

if str(_backend_root) not in __path__:
    __path__.append(str(_backend_root))
