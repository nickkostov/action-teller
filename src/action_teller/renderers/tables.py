from typing import List, Tuple

def to_table(rows: List[Tuple[str, str]], headers: Tuple[str, str]) -> str:
    if not rows:
        return "_None_"
    lines = [f"| {headers[0]} | {headers[1]} |", "|---|---|"]
    for k, v in rows:
        v = str(v).replace("\n", "<br/>")
        lines.append(f"| `{k}` | {v} |")
    return "\n".join(lines)
