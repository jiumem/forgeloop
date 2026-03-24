from __future__ import annotations

import sys
from pathlib import Path

def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in [current.parent, *current.parents]:
        if (candidate / ".codex").exists() and (candidate / ".agents").exists():
            return candidate
    return Path(__file__).resolve().parents[5]

repo_root = _repo_root()
sys.path.insert(0, str(repo_root / "src"))

from codex_initiative_runtime.cli import main as cir_main

if __name__ == "__main__":
    raise SystemExit(cir_main(['prepare-review-bundle'] + sys.argv[1:]))
