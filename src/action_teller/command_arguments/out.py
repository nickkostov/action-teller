import click
from pathlib import Path

def out_option(f):
    return click.option(
        "--out", "-o",
        required=True,
        type=click.Path(path_type=Path),
        help="Output directory for Markdown files."
    )(f)
