#!/usr/bin/env python3
import click
from .providers.github_cli import github_cli


class ProviderGroup(click.Group):
    """Custom command group that intercepts unsupported providers."""

    def get_command(self, ctx, cmd_name):
        # allow known provider
        if cmd_name in ("github",):
            return super().get_command(ctx, cmd_name)

        # show custom unsupported-provider error
        raise click.UsageError(
            f"Unsupported CI/CD provider: '{cmd_name}'. Only 'github' is supported."
        )


@click.group(
    cls=ProviderGroup,
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.pass_context
def cifolio(ctx):
    """
    CIFolio — CI/CD documentation and linting CLI.

    Usage:
      cifolio <provider> [OPTIONS]

    Supported providers:
      github   Work with GitHub Actions and Workflows.

    Example:
      cifolio github --workflow . --out docs
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# register supported provider
cifolio.add_command(github_cli, "github")


@click.version_option(version="0.3.0", prog_name="cifolio")
def version():
    """Display version."""
    pass


if __name__ == "__main__":
    cifolio()
