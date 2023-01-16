

about_info = {
    'name': 'Sparkle',
    'version': 0.4
}

about_str = '{name}-{version}'.format(**about_info)


def print_about():
    print(about_str)
