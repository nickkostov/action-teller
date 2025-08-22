from .tables import to_table

def render(inputs: dict) -> str:
    rows = []
    for key, meta in (inputs or {}).items():
        desc = (meta or {}).get("description", "").strip()
        req = (meta or {}).get("required", False)
        default = (meta or {}).get("default", "")
        deprec = (meta or {}).get("deprecationMessage", "")
        bits = []
        if desc: bits.append(desc)
        bits.append(f"**required:** `{str(req).lower()}`")
        if default != "": bits.append(f"**default:** `{default}`")
        if deprec: bits.append(f"**deprecated:** {deprec}")
        rows.append((key, "<br/>".join(bits)))
    return to_table(rows, ("input", "details"))
