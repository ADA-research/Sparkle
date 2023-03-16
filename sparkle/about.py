"""Helper module for information about Sparkle."""

about_info = {
    "name": "Sparkle",
    "version": 0.5
}

about_str = f"{about_info['name']}-{about_info['version']}"


def print_about() -> None:
    """Print the about str."""
    print(about_str)
