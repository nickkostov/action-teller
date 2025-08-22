import click

def confluence_option(f):
    return click.option(
        "--confluence",
        is_flag=True,
        help="Confluence-friendly Markdown (plain tables)."
    )(f)
