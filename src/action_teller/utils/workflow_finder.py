from pathlib import Path
from typing import List

# Detect any YAML file. We filter by content later.
CANDIDATE_EXTS = {".yml", ".yaml"}

def find_workflow_files(root: Path) -> List[Path]:
    """
    Return *.yml/*.yaml files anywhere under root.
    The caller will open and verify they are workflows (contain 'on' and 'jobs').
    """
    if root.is_file():
        return [root] if root.suffix.lower() in CANDIDATE_EXTS else []
    return [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in CANDIDATE_EXTS
    ]
