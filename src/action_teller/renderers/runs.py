def render(runs: dict) -> str:
    if not runs:
        return "_None_"
    using = runs.get("using", "")
    md = [f"**using:** `{using}`"]
    if using == "composite":
        steps = runs.get("steps", []) or []
        if not steps:
            md.append("- _No steps defined_")
        else:
            md.append("### Steps")
            for i, s in enumerate(steps, start=1):
                name = s.get("name") or s.get("id") or f"step-{i}"
                md.append(f"- **{name}**")
                if s.get("id"):
                    md.append(f"  - id=`{s['id']}`")
                if s.get("if"):
                    md.append(f"  - if=`{s['if']}`")
                if s.get("shell"):
                    md.append(f"  - shell=`{s['shell']}`")
                if s.get("uses"):
                    uses_val = s["uses"]
                    md.append(f"  - uses=`{uses_val}`")
                    if "@" in uses_val:
                        _, version = uses_val.split("@", 1)
                        md.append(f"  - version=`{version}`")
                if s.get("run"):
                    run_cmd = str(s["run"]).strip()
                    indent = " " * 6
                    md.append(
                        "  - run:\n\n"
                        + f"{indent}```bash\n"
                        + "\n".join(f"{indent}{line}" for line in run_cmd.splitlines())
                        + f"\n{indent}```"
                    )
    elif isinstance(using, str) and using.startswith("node"):
        main = runs.get("main", "")
        pre = runs.get("pre", "")
        post = runs.get("post", "")
        md.append(f"- **main:** `{main}`")
        if pre:
            md.append(f"- **pre:** `{pre}`")
        if post:
            md.append(f"- **post:** `{post}`")
    elif using == "docker":
        image = runs.get("image", "")
        entry = runs.get("entrypoint", "")
        args = runs.get("args", [])
        md.append(f"- **image:** `{image}`")
        if entry:
            md.append(f"- **entrypoint:** `{entry}`")
        if args:
            md.append(f"- **args:** `{args}`")
    else:
        md.append("_Unknown `using` type_")
    return "\n".join(md)
