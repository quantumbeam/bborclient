from typing import BinaryIO
from .conf import API_URL_DOCKER, API_URL_LOCAL, API_URL_MDX


def get_file_size_from_binaryio(bytes: BinaryIO) -> int:
    """
    Get the size of a file from a BinaryIO object.
    
    Args:
        bytes (BinaryIO): The BinaryIO object representing the file.
        
    Returns:
        int: The size of the file in bytes.
    """
    if bytes is None:
        return 0
    current_position = bytes.tell()  # Save current position
    bytes.seek(0, 2)  # Move to end of file
    size = bytes.tell()  # Get size
    bytes.seek(current_position)  # Restore original position
    return size


def api_url(server:str='mdx'):
    if server=='mdx':
        return API_URL_MDX
    elif server=='local':
        return API_URL_LOCAL
    elif server=='docker':
        return API_URL_DOCKER
    else:
        raise ValueError('The argument server should be either "mdx", "local", or "docker".')


def require_token(func):
    def wrapper(self, *args, **kwargs):
        if self.token:
            return func(self, *args, **kwargs)
        else:
            raise ValueError('Token is empty')
    return wrapper
