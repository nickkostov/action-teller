import re
import yaml
from pathlib import Path
from typing import Any, Dict

# YAML 1.2-like SafeLoader: only "true"/"false" are booleans
class Yaml12SafeLoader(yaml.SafeLoader):  # <-- added
    pass

# remove the broad YAML 1.1 bool resolver (yes/no/on/off/…)
for first, mappings in list(Yaml12SafeLoader.yaml_implicit_resolvers.items()):  # <-- added
    Yaml12SafeLoader.yaml_implicit_resolvers[first] = [
        (tag, reg) for (tag, reg) in mappings if tag != 'tag:yaml.org,2002:bool'
    ]

# add a strict boolean resolver: only true|false (case-insensitive)
Yaml12SafeLoader.add_implicit_resolver(  # <-- added
    'tag:yaml.org,2002:bool',
    re.compile(r'^(?:true|false)$', re.IGNORECASE),
    list('tTfF')
)

def parse_action_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        # use Yaml12SafeLoader to keep "on" as a string key
        return yaml.load(f, Loader=Yaml12SafeLoader) or {}  # <-- changed
