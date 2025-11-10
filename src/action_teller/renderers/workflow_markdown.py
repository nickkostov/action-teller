from pathlib import Path
from typing import Dict, Any, Optional, Set, List, Tuple
import re
import json

# Simple helpers to keep consistent formatting within this module.

def _h2(title: str) -> str:
    return f"## {title}\n"

def _h3(title: str) -> str:
    return f"### {title}\n"

def _h4(title: str) -> str:
    return f"#### {title}\n"

def _table(rows: List[Tuple[str, str]], headers: Tuple[str, str]) -> str:
    if not rows:
        return "_None_"
    lines = [f"| {headers[0]} | {headers[1]} |", "|---|---|"]
    for k, v in rows:
        v = str(v).replace("\n", "<br/>")
        lines.append(f"| `{k}` | {v} |")
    return "\n".join(lines)

def _stringify_yaml(yaml_obj: Any) -> str:
    try:
        # Dump to JSON-like string for stable searching.
        return json.dumps(yaml_obj, ensure_ascii=False, indent=2)
    except Exception:
        return str(yaml_obj)

_expr_pattern = re.compile(r"\${{\s*([^}]+)\s*}}")
_token_pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")

# Roots considered as GitHub Contexts per docs
KNOWN_CONTEXT_ROOTS = {
    "github", "env", "secrets", "vars", "runner", "job", "steps", "needs",
    "matrix", "strategy", "inputs", "hashFiles", "fromJSON", "toJSON",
    "always", "cancelled", "success", "failure", "format", "startsWith",
    "endsWith", "contains", "join"
}

def _collect_expressions(raw: str) -> List[str]:
    return [m.group(1) for m in _expr_pattern.finditer(raw)]

def _collect_context_roots(exprs: List[str]) -> Set[str]:
    roots: Set[str] = set()
    for e in exprs:
        # Take the first identifier token in the expression as a candidate root
        for t in _token_pattern.findall(e):
            if t in KNOWN_CONTEXT_ROOTS:
                roots.add(t)
                break
    return roots

def _collect_dotted_refs(raw: str, prefix: str) -> Set[str]:
    # Find occurrences like secrets.MY_TOKEN, vars.MY_VAR
    pattern = re.compile(rf"{re.escape(prefix)}\.([A-Za-z_][A-Za-z0-9_]*)")
    return set(pattern.findall(raw))

def _list_on_triggers(on_field: Any) -> List[str]:
    if isinstance(on_field, dict):
        return sorted(on_field.keys())
    if isinstance(on_field, list):
        return [str(x) for x in on_field]
    if isinstance(on_field, str):
        return [on_field]
    return []

def _gather_inputs(data: Dict[str, Any]) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []

    # workflow_dispatch.inputs
    wd = ((data.get("on") or {}).get("workflow_dispatch") or {})
    wd_inputs = (wd.get("inputs") or {})
    for k, v in wd_inputs.items():
        desc = (v or {}).get("description", "") or ""
        req = str((v or {}).get("required", False)).lower()
        default = (v or {}).get("default", "")
        bits = []
        if desc:
            bits.append(desc)
        bits.append(f"**required:** `{req}`")
        if default != "":
            bits.append(f"**default:** `{default}`")
        rows.append((k, "<br/>".join(bits)))

    # workflow_call.inputs (reusable workflows)
    wc = ((data.get("on") or {}).get("workflow_call") or {})
    wc_inputs = (wc.get("inputs") or {})
    for k, v in wc_inputs.items():
        desc = (v or {}).get("description", "") or ""
        req = str((v or {}).get("required", False)).lower()
        default = (v or {}).get("default", "")
        bits = []
        if desc:
            bits.append(desc)
        bits.append(f"**required:** `{req}`")
        if default != "":
            bits.append(f"**default:** `{default}`")
        rows.append((k, "<br/>".join(bits)))

    return rows

def _gather_steps(data: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    jobs = data.get("jobs") or {}
    for job_id, job in jobs.items():
        job_name = job.get("name") or job_id
        lines.append(f"- **Job:** `{job_name}`")
        # Reusable workflow invocation
        if "uses" in job:
            lines.append(f"  - uses=`{job['uses']}`")
            if job.get("with"):
                lines.append(f"  - with: `{job['with']}`")
            continue
        steps = job.get("steps") or []
        if not steps:
            lines.append("  - _No steps_")
            continue
        for i, s in enumerate(steps, start=1):
            step_name = s.get("name") or s.get("id") or f"step-{i}"
            lines.append(f"  - **Step:** {step_name}")
            if s.get("id"):
                lines.append(f"    - id=`{s['id']}`")
            if s.get("if"):
                lines.append(f"    - if=`{s['if']}`")
            if s.get("uses"):
                lines.append(f"    - uses=`{s['uses']}`")
            if s.get("run"):
                run_cmd = str(s["run"]).strip()
                indent = " " * 6
                lines.append(
                    "    - run:\n\n"
                    + f"{indent}```bash\n"
                    + "\n".join(f"{indent}{line}" for line in run_cmd.splitlines())
                    + f"\n{indent}```"
                )
    return lines

def _gather_secrets(data: Dict[str, Any], raw: str) -> List[str]:
    found: Set[str] = set()
    # From workflow_call.secrets
    wc = ((data.get("on") or {}).get("workflow_call") or {})
    wc_secrets = (wc.get("secrets") or {})
    for k in wc_secrets.keys():
        found.add(k)
    # Any secrets.<NAME> usages across the file
    found.update(_collect_dotted_refs(raw, "secrets"))
    return sorted(found)

def _gather_variables(raw: str) -> List[str]:
    # Find vars.<NAME> references
    return sorted(_collect_dotted_refs(raw, "vars"))

def _gather_contexts(raw: str) -> List[str]:
    exprs = _collect_expressions(raw)
    roots = _collect_context_roots(exprs)
    return sorted(roots)

def render_workflow_doc(
    data: Dict[str, Any],
    file_path: Path,
    llm_summary: bool = False,
    llm_model: str = "mistral",
    summarize_fn: Optional[callable] = None,
) -> str:
    """
    Render a single workflow file into Markdown with the required structure.
    """
    md: List[str] = []

    # Title as H1 equals filename for clarity
    md.append(f"# {file_path.stem}\n")

    # Section: File
    md.append(_h2("File"))
    md.append(f"{file_path.name}\n")  # exact filename

    # Section: Conditions to run
    md.append(_h3("Conditions to run:"))
    triggers = _list_on_triggers(data.get("on"))
    if triggers:
        md.append("- " + "\n- ".join(f"`{t}`" for t in triggers) + "\n")
    else:
        md.append("_None_\n")

    # Section: Inputs
    md.append(_h4("Inputs"))
    inputs_rows = _gather_inputs(data)
    md.append(_table(inputs_rows, ("input", "details")) + "\n")

    # Section: Purpose summary (AI)
    md.append(_h3("Purpose summary:"))
    if llm_summary and summarize_fn:
        # Construct a compact prompt based on workflow attributes
        compact = {
            "name": data.get("name", file_path.stem),
            "on": triggers,
            "jobs": list((data.get("jobs") or {}).keys()),
        }
        # Reuse existing summarize function signature
        try:
            summary = summarize_fn(
                {
                    "name": compact["name"],
                    "description": "GitHub Actions workflow",
                    "inputs": {"workflow_inputs": {k: {} for k, _ in inputs_rows}},
                    "outputs": {},
                    "triggers": compact["on"],
                    "jobs": compact["jobs"],
                },
                model=llm_model,
            )
        except Exception as e:
            summary = f"_(Ollama error: {e})_"
        if summary:
            md.append(summary + "\n")
        else:
            md.append("_(LLM produced no summary)_\n")
    else:
        md.append("_(LLM summary disabled)_\n")

    # Section: Steps completed
    md.append(_h4("Steps completed:"))
    step_lines = _gather_steps(data)
    md.append("\n".join(step_lines) + ("\n" if step_lines else "_None_\n"))

    # Prepare raw text for scanning secrets/vars/contexts
    raw = _stringify_yaml(data)

    # Section: Secrets used
    md.append(_h3("Secrets used in the file"))
    secrets_list = _gather_secrets(data, raw)
    if secrets_list:
        md.append("- " + "\n- ".join(f"`{s}`" for s in secrets_list) + "\n")
    else:
        md.append("_None_\n")

    # Section: Variables used
    md.append(_h3("Variables used in the file"))
    vars_list = _gather_variables(raw)
    if vars_list:
        md.append("- " + "\n- ".join(f"`{v}`" for v in vars_list) + "\n")
    else:
        md.append("_None_\n")

    # Section: GitHub Contexts used
    md.append(_h3("GitHub Contexts used"))
    ctxs = _gather_contexts(raw)
    if ctxs:
        md.append("- " + "\n- ".join(f"`{c}`" for c in ctxs) + "\n")
    else:
        md.append("_None_\n")

    md.append("\n---\n_Generated by action-teller_")
    return "\n".join(md)
