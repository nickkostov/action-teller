import click

def ai_summary_option(f):
    f = click.option(
        "--ai-summary",
        is_flag=True,
        help="Generate a short AI-based summary using a local model via Ollama.",
    )(f)
    f = click.option(
        "--model",
        default="mistral",
        show_default=True,
        help="Name of the local Ollama model to use (e.g., mistral, codellama).",
    )(f)
    return f
