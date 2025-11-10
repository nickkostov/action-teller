from typing import Dict, Any, List

def render_workflow_markdown(data: Dict[str, Any]) -> str:
    """
    Render a Markdown summary for a GitHub workflow.
    Includes triggers, inputs, jobs, secrets, variables, and contexts.
    """

    md: List[str] = []

    # --- File triggers ---
    on_section = data.get("on", {})
    if on_section:
        md.append("### Conditions to run")
        if isinstance(on_section, dict):
            triggers = ", ".join(on_section.keys())
            md.append(f"- Triggered on: **{triggers}**")
        elif isinstance(on_section, list):
            md.append(f"- Triggered on: **{', '.join(on_section)}**")
        else:
            md.append(f"- Triggered on: **{on_section}**")

    # --- Inputs ---
    workflow_call = on_section.get("workflow_call", {}) if isinstance(on_section, dict) else {}
    inputs = workflow_call.get("inputs", {})
    if inputs:
        md.append("\n### Inputs")
        for name, meta in inputs.items():
            desc = meta.get("description", "")
            md.append(f"- `{name}` — '{desc}'")

    # --- Secrets ---
    secrets = workflow_call.get("secrets", {})
    if secrets:
        md.append("\n### Secrets used")
        for name, meta in secrets.items():
            desc = meta.get("description", "")
            md.append(f"- `{name}` — '{desc}'")

    # --- Jobs ---
    jobs = data.get("jobs", {})
    if jobs:
        md.append("\n### Steps completed")
        for job_name, job_data in jobs.items():
            job_title = job_data.get("name", job_name)
            md.append(f"- **Job:** \"{job_title}\"")

            if "uses" in job_data:
                used = job_data["uses"]
                md.append(f"  - uses: '{used}'")

            steps = job_data.get("steps", [])
            for step in steps:
                step_name = step.get("name") or step.get("id")
                if step_name:
                    md.append(f"  - Step: \"{step_name}\"")
                if "uses" in step:
                    md.append(f"    - uses: '{step['uses']}'")
                if "run" in step:
                    md.append("    - run command present")

    # --- Variables ---
    if "env" in data:
        md.append("\n### Variables used")
        for k, v in data["env"].items():
            md.append(f"- `{k}` = `{v}`")

    # --- Contexts (detected heuristically) ---
    all_text = str(data)
    contexts = [
        ctx
        for ctx in ["github", "env", "secrets", "vars", "inputs"]
        if f"${{{{ {ctx}." in all_text
    ]
    if contexts:
        md.append("\n### GitHub Contexts used")
        md.append(", ".join(f"`{c}`" for c in contexts))

    return "\n".join(md)
