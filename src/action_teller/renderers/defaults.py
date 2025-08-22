from .tables import to_table

def render(defaults: dict) -> str:
    if not defaults:
        return "_None_"
    blocks = []
    for k, v in defaults.items():
        if isinstance(v, dict):
            rows = [(kk, str(vv)) for kk, vv in v.items()]
            blocks.append(f"**{k}**\n\n{to_table(rows, ('key', 'value'))}")
        else:
            blocks.append(f"- **{k}:** `{v}`")
    return "\n\n".join(blocks)
