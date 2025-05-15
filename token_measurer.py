# import tiktoken

# prompt_file = "/Users/admin/Documents/LLM_Eval/SOLOBench/SOLO_Bench_Input.txt"

# with open(prompt_file, "r") as f:
#     full_prompt = f.read()

# enc = tiktoken.encoding_for_model(tiktoken.get_encoding("gemma3"))
# tokens = enc.encode(full_prompt)
# print(len(tokens))


#!/usr/bin/env python3
import subprocess
import sys


def get_installed_models():
    """Return a list of model names as reported by `ollama list`."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error running `ollama list`: {e}\n")
        sys.exit(1)

    models = []
    for line in result.stdout.splitlines():
        line = line.strip()
        # Skip header or empty lines
        if not line or line.lower().startswith("name"):
            continue
        # First column is NAME (e.g. "gemma-3-4b-it-50k:latest")
        parts = line.split()
        models.append(parts[0])
    return models


def get_context_size(model_name):
    """Return the context length for a given model, or None if not found."""
    try:
        result = subprocess.run(
            ["ollama", "show", model_name],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return None

    for line in result.stdout.splitlines():
        line = line.strip()
        # Look for the "context length" field
        if line.startswith("context length"):
            # e.g. "context length      131072"
            parts = line.split()
            return parts[-1]
    return None


def main():
    models = get_installed_models()
    if not models:
        print("No models found.")
        return

    for model in models:
        ctx = get_context_size(model)
        if ctx:
            print(f"{model} - {ctx}")
        else:
            print(f"{model} - (context length not found)")


if __name__ == "__main__":
    main()
