def ollama_summarize(data: dict, model: str = "mistral") -> str:
    """Use Ollama locally to summarize a GitHub Action."""
    try:
        import ollama
    except ImportError:
        return "_(Ollama not installed)_"

    prompt = f"""You are documenting a GitHub Action.
Name: {data.get("name")}
Description: {data.get("description")}
Inputs: {list((data.get("inputs") or {}).keys())}
Outputs: {list((data.get("outputs") or {}).keys())}

Write a 2-3 sentence human-friendly summary of what this Action does."""

    try:
        resp = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        return f"_(Ollama error: {e})_"
