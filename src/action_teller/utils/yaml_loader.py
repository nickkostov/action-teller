import yaml
from pathlib import Path
from typing import Any, Dict

def parse_action_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
