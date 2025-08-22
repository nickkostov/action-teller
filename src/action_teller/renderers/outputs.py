from .tables import to_table

def render(outputs: dict) -> str:
    rows = []
    for key, meta in (outputs or {}).items():
        desc = (meta or {}).get("description", "").strip()
        val = (meta or {}).get("value", "")
        bits = []
        if desc:
            bits.append(desc)
        if val != "":
            bits.append(f"**value:** `{val}`")
        rows.append((key, "<br/>".join(bits)))
    return to_table(rows, ("output", "details"))
