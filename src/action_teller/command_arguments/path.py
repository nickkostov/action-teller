import click
from pathlib import Path

def path_argument(f):
    return click.argument(
        "path",
        type=click.Path(exists=True, path_type=Path)
    )(f)
