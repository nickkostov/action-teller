import click
from pathlib import Path

# utils
from ..utils.file_finder import find_action_files
from ..utils.workflow_finder import find_workflow_files
from ..utils.yaml_loader import parse_action_yaml
from ..utils.ollama import ollama_summarize
from ..utils.lint_ci import lint_files

# renderers
from ..renderers import branding, inputs, outputs, runs, permissions, env, defaults
from ..renderers.workflow_markdown import render_workflow_markdown
from ..renderers.mermaid_diagram import render_mermaid, write_mermaid_file
from ..renderers.workflow_markdown import render_workflow_markdown


@click.command(
    name="github",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("--workflow", multiple=True, help="Path(s) to workflow file(s) or '.' for all workflows.")
@click.option("--action", multiple=True, help="Path(s) to action file(s) or '.' for all actions.")
@click.option("--out", "-o", type=click.Path(path_type=Path), default=Path("cifolio"), help="Output directory for Markdown files.")
@click.option("--ai-sum", is_flag=True, help="Generate AI-based summaries using Ollama.")
@click.option("--ai-model", default="mistral", help="Model to use with Ollama (default: mistral).")
@click.option("--lint-ci", default=None, help="Validate and format CI/CD YAML files for given provider (github).")
@click.option("--docs", is_flag=True, help="Show documentation links for GitHub Actions.")
@click.option("--index", is_flag=True, help="Generate index.md file for generated documentation.")
@click.option("--diagram", is_flag=True, help="Generate a Mermaid diagram of workflow job dependencies.")
def github_cli(workflow, action, out, ai_sum, ai_model, lint_ci, docs, index, diagram):
    """
    Work with GitHub Actions and Workflows.

    Examples:
      cifolio github --workflow . --out docs
      cifolio github --workflow . --ai-sum --ai-model mistral
      cifolio github --lint-ci github --workflow .
      cifolio github --workflow . --diagram --out docs
    """

    out.mkdir(parents=True, exist_ok=True)

    # --- Documentation flag only ---
    if docs:
        click.echo("GitHub Actions documentation:")
        click.echo("- Workflows: https://docs.github.com/en/actions/using-workflows")
        click.echo("- Actions:   https://docs.github.com/en/actions/creating-actions")
        return

    # --- Lint mode ---
    if lint_ci:
        if lint_ci.lower() != "github":
            raise click.UsageError(f"--lint-ci must equal provider 'github', not '{lint_ci}'")

        lint_targets = []

        if workflow:
            for wf in workflow:
                path = Path(wf)
                if wf == ".":
                    lint_targets.extend(find_workflow_files(Path(".")))
                elif path.is_dir():
                    lint_targets.extend(find_workflow_files(path))
                elif path.is_file():
                    lint_targets.append(path)

        if action:
            for act in action:
                path = Path(act)
                if act == ".":
                    lint_targets.extend(find_action_files(Path(".")))
                elif path.is_dir():
                    lint_targets.extend(find_action_files(path))
                elif path.is_file():
                    lint_targets.append(path)

        if not lint_targets:
            raise click.UsageError("No files found to lint. Use --workflow or --action with paths or '.'.")

        click.echo(f"Linting {len(lint_targets)} YAML file(s)...\n")
        lint_files(lint_targets)
        return

    # --- AI flag sanity check ---
    if ai_model and not ai_sum:
        click.echo(f"Note: --ai-model '{ai_model}' specified but --ai-sum not enabled. AI summaries disabled.", err=True)

    # --- Find workflows ---
    workflow_files = []
    if workflow:
        for wf in workflow:
            path = Path(wf)
            if wf == ".":
                workflow_files.extend(find_workflow_files(Path(".")))
            elif path.is_dir():
                workflow_files.extend(find_workflow_files(path))
            elif path.is_file():
                workflow_files.append(path)

    # --- Find actions ---
    action_files = []
    if action:
        for ac in action:
            path = Path(ac)
            if ac == ".":
                action_files.extend(find_action_files(Path(".")))
            elif path.is_dir():
                action_files.extend(find_action_files(path))
            elif path.is_file():
                action_files.append(path)

    if not workflow_files and not action_files:
        raise click.UsageError("No workflows or actions found. Use --workflow or --action with paths or '.'.")

    # --- Process workflows ---
    for f in workflow_files:
        try:
            data = parse_action_yaml(f)
        except Exception as e:
            click.echo(f"[ERROR] Failed to parse {f}: {e}", err=True)
            continue

        name = data.get("name", f.stem)
        desc = data.get("description", "")

        md = [f"# {name}\n"]
        if desc:
            md.append(desc + "\n")

        md.append(f"**File:** `{f}`\n")

        if ai_sum:
            summary = ollama_summarize(data, model=ai_model)
            if summary:
                md.append(f"### Purpose summary\n> {summary}\n")

        md.append(render_workflow_markdown(data))

        if diagram:
            md.append("\n### Workflow Diagram\n")
            md.append(render_mermaid(data, workflow_name=f.name))
            write_mermaid_file(f, data, out)

        out_file = out / f"{f.stem}.md"
        out_file.write_text("\n".join(md), encoding="utf-8")
        click.echo(f"Wrote workflow doc: {out_file}")

    # --- Process actions ---
    for f in action_files:
        try:
            data = parse_action_yaml(f)
        except Exception as e:
            click.echo(f"[ERROR] Failed to parse {f}: {e}", err=True)
            continue

        name = data.get("name", f.parent.name)
        desc = data.get("description", "")
        author = data.get("author", "")

        md = [f"# {name}\n"]
        if desc:
            md.append(desc + "\n")
        md.append(f"**File:** `{f}`  ")
        if author:
            md.append(f"**Author:** `{author}`  ")

        if ai_sum:
            summary = ollama_summarize(data, model=ai_model)
            if summary:
                md.append(f"\n### Purpose summary\n> {summary}\n")

        md.append("\n## Branding\n" + branding.render(data.get("branding", {})))
        md.append("\n## Inputs\n" + inputs.render(data.get("inputs", {})))
        md.append("\n## Outputs\n" + outputs.render(data.get("outputs", {})))
        md.append("\n## Runs\n" + runs.render(data.get("runs", {})))
        md.append("\n## Permissions\n" + permissions.render(data.get("permissions", {})))
        md.append("\n## Env\n" + env.render(data.get("env", {})))
        md.append("\n## Defaults\n" + defaults.render(data.get("defaults", {})))
        md.append("\n---\n_Generated by cifolio_")

        out_file = out / f"{f.stem}.md"
        out_file.write_text("\n".join(md), encoding="utf-8")
        click.echo(f"Wrote action doc: {out_file}")

    # --- Optional index file ---
    if index:
        index_path = out / "INDEX.md"
        lines = ["# CI/CD Documentation Index", ""]
        for md_file in sorted(out.glob("*.md")):
            if md_file.name.lower() != "index.md":
                lines.append(f"- [{md_file.stem}]({md_file.name})")
        index_path.write_text("\n".join(lines), encoding="utf-8")
        click.echo(f"Wrote {index_path}")
