# Custom Linter for GitHub Actions Workflows and Actions
import re
import yaml
from pathlib import Path
from typing import List, Any
from yaml.nodes import MappingNode


# --- regex for ${{ ... }} expressions ---
GITHUB_EXPR = re.compile(r"\$\{\{\s*([^}]*)\s*\}\}")
# --- reusable workflow/action detection pattern ---
REUSABLE_PATTERN = re.compile(r"\.github/workflows/|^[\w\-/]+@[\w.\-]+$")


class GithubStyleDumper(yaml.SafeDumper):
    """Custom YAML dumper preserving GitHub workflow semantics and enforcing quoting rules."""

    def represent_mapping(self, tag, mapping, flow_style=None):
        value = []
        for key, val in mapping.items():
            key_node = self.represent_data(key)
            self._current_key = key
            val_node = self.represent_data(val)
            self._current_key = None
            value.append((key_node, val_node))
        return MappingNode(tag, value, flow_style=flow_style)

    def represent_scalar(self, tag, value: Any, style: str = None):
        # Preserve block scalars for multiline text
        if isinstance(value, str) and "\n" in value:
            style = "|"

        key = getattr(self, "_current_key", None)

        # Double quotes for all name fields
        if key == "name":
            style = '"'
        # Single quotes for reusable uses:
        elif key == "uses" and isinstance(value, str) and REUSABLE_PATTERN.search(value):
            style = "'"
        # Single quotes for workflow_call input descriptions
        elif key == "description" and isinstance(value, str):
            style = "'"

        return super().represent_scalar(tag, value, style)


def _restore_github_spacing(text: str) -> str:
    """Normalize ${{ ... }} expressions to include single spaces."""
    return GITHUB_EXPR.sub(lambda m: f"${{{{ {m.group(1).strip()} }}}}", text)


def _validate_workflow_structure(data: dict, file: Path) -> bool:
    ok = True
    if "on" not in data:
        print(f"[WARN] {file}: missing required key 'on'")
        ok = False
    if "jobs" not in data:
        print(f"[WARN] {file}: missing required key 'jobs'")
        ok = False
    else:
        jobs = data["jobs"]
        if not isinstance(jobs, dict) or not jobs:
            print(f"[WARN] {file}: 'jobs' must be a non-empty mapping")
            ok = False
        else:
            for job_name, job in jobs.items():
                if "steps" not in job and "uses" not in job:
                    print(f"[WARN] {file}: job '{job_name}' missing 'steps' or 'uses'")
                    ok = False
                elif "uses" in job and REUSABLE_PATTERN.search(str(job["uses"])):
                    print(f"[INFO] {file}: job '{job_name}' uses reusable workflow '{job['uses']}'")
                elif "steps" in job:
                    for step in job.get("steps", []):
                        if isinstance(step, dict) and "uses" in step and REUSABLE_PATTERN.search(str(step["uses"])):
                            print(f"[INFO] {file}: step uses reusable action '{step['uses']}'")
    return ok


def lint_yaml_file(file_path: Path) -> bool:
    """Validate and format a GitHub workflow or action YAML file."""
    try:
        src_text = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(src_text)
    except yaml.YAMLError as e:
        print(f"[ERROR] {file_path}: invalid YAML — {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        return False

    if not isinstance(data, dict):
        print(f"[WARN] {file_path}: top-level not a mapping, skipped.")
        return False

    valid = _validate_workflow_structure(data, file_path)

    formatted = yaml.dump(
        data,
        Dumper=GithubStyleDumper,
        sort_keys=False,
        indent=2,
        width=120,
        allow_unicode=True,
        default_flow_style=False,
    )

    formatted = _restore_github_spacing(formatted).rstrip() + "\n"

    file_path.write_text(formatted, encoding="utf-8")
    print(f"[OK] {file_path} linted and formatted (GitHub compliant).")
    return valid


def lint_files(files: List[Path]) -> None:
    """Lint multiple YAML files and show summary."""
    ok, fail = 0, 0
    for f in files:
        if lint_yaml_file(f):
            ok += 1
        else:
            fail += 1
    print(f"\nLint summary: {ok} valid, {fail} failed.\n")
