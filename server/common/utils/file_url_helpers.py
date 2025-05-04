from server.settings.components import config


def get_full_url(file_url: str | None) -> str | None:
    """
    Concatenates the DOMAIN_NAME environment variable with a file or image URL
    to create a complete file path.

    Args:
        file_url (str): The relative URL of the file/image

    Returns:
        str: The complete URL with domain name prepended

    Examples:
        >>> get_full_url('/media/users/image.jpg')
        'http://localhost:8000/media/users/image.jpg'
    """
    if not file_url:
        return None

    domain: str = config('DOMAIN_NAME', default='', cast=str)  # type: ignore

    # Remove any leading slash from file_url if domain already ends with slash
    if domain.endswith('/') and file_url.startswith('/'):
        file_url = file_url[1:]
    # Add slash between domain and file_url if neither has it
    elif not domain.endswith('/') and not file_url.startswith('/'):
        domain = f'{domain}/'

    return f'{domain}{file_url}'
