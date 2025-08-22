from .tables import to_table

def render(branding: dict) -> str:
    if not branding:
        return "_None_"
    rows = [(k, str(v)) for k, v in branding.items()]
    return to_table(rows, ("key", "value"))
