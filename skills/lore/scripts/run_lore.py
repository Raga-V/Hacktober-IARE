"""Run the Lore CLI from the skill folder.

Uses the `lore` package from the Lore repository this skill lives in (skills/lore/scripts/ -> repo root),
or an installed copy (`pip install git+https://github.com/Raga-V/Hacktober-IARE`).
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if (repo_root / "lore" / "__main__.py").exists():
    sys.path.insert(0, str(repo_root))

try:
    from lore.__main__ import main
except ImportError:
    sys.exit("Lore is not installed. Run: pip install git+https://github.com/Raga-V/Hacktober-IARE")

main()
