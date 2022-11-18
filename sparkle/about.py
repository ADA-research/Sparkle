"""Helper module for information about Sparkle."""

about_info = {
    'name': 'Sparkle',
    'version': 0.3
}

about_str = '{name}-{version}'.format(**about_info)


def print_about() -> None:
    """Print the about str."""
    print(about_str)
