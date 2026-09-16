from importlib.metadata import version as _get_version
from .client import BBORClient

__version__ = _get_version(__package__ or 'bbor_client')


__all__ = [
    'BBORClient',
    '__version__',
]

