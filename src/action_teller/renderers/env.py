from .tables import to_table

def render(env: dict) -> str:
    if not env:
        return "_None_"
    rows = [(k, str(v)) for k, v in env.items()]
    return to_table(rows, ("env var", "value"))
