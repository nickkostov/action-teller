from pathlib import Path
from typing import Dict, Any, List


def render_mermaid(workflow_data: Dict[str, Any], workflow_name: str = "") -> str:
    """
    Render a Mermaid flowchart of job dependencies for a GitHub workflow.

    The diagram is derived from the 'jobs' section:
      jobs:
        build:
        test:
          needs: build
        deploy:
          needs: [test]

    Produces:
    ```mermaid
    flowchart TD
        build["build"]
        test["test"]
        deploy["deploy"]
        build --> test
        test --> deploy
    ```
    """

    jobs = workflow_data.get("jobs", {})
    if not isinstance(jobs, dict) or not jobs:
        return "_No jobs found for diagram generation_"

    lines: List[str] = []
    lines.append("```mermaid")
    lines.append("flowchart TD")

    # Create job nodes
    for job_name, job_body in jobs.items():
        label = job_body.get("name", job_name)
        label = label.replace('"', "'")  # escape inner quotes
        lines.append(f'    {job_name}["{label}"]')

    # Draw arrows (dependencies)
    for job_name, job_body in jobs.items():
        needs = job_body.get("needs")
        if not needs:
            continue
        if isinstance(needs, str):
            lines.append(f"    {needs} --> {job_name}")
        elif isinstance(needs, list):
            for n in needs:
                lines.append(f"    {n} --> {job_name}")

    # Footer comment
    lines.append("")
    lines.append(f"    %% Diagram generated for workflow: {workflow_name}")
    lines.append("```")

    return "\n".join(lines)


def write_mermaid_file(workflow_path: Path, workflow_data: Dict[str, Any], out_dir: Path) -> Path:
    """
    Generate and save a standalone Mermaid Markdown file for the given workflow.

    Output file:
      <out_dir>/<workflow_name>_diagram.md
    """
    diagram_md = render_mermaid(workflow_data, workflow_name=workflow_path.name)
    out_file = out_dir / f"{workflow_path.stem}_diagram.md"
    out_file.write_text(diagram_md, encoding="utf-8")
    return out_file
