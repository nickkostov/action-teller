import click

def llm_summary_option(f):
    f = click.option(
        "--llm-summary",
        is_flag=True,
        help="Generate a short summary using Ollama."
    )(f)
    f = click.option(
        "--llm-model",
        default="mistral",
        help="Ollama model to use (default: mistral)."
    )(f)
    return f
