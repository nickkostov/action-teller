import click

def single_option(f):
    return click.option(
        "--single",
        is_flag=True,
        help="Write a single README.md instead of one file per action."
    )(f)
