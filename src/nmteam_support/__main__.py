"""Entry point: ``uv run python -m nmteam_support`` regenerates the site."""

from nmteam_support.generator import default_options, generate

if __name__ == "__main__":
    generate(default_options())
