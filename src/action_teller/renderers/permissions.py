from .tables import to_table

def render(perms: dict) -> str:
    if not perms:
        return "_None_"
    rows = [(k, str(v).lower()) for k, v in perms.items()]
    return to_table(rows, ("permission", "access"))
