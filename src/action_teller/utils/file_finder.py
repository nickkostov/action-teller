from pathlib import Path
from typing import List

YAML_FILENAMES = {"action.yml", "action.yaml"}

def find_action_files(root: Path) -> List[Path]:
    if root.is_file():
        return [root] if root.name in YAML_FILENAMES else []
    return [p for p in root.rglob("*") if p.is_file() and p.name in YAML_FILENAMES]
