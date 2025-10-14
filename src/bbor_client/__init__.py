from importlib.metadata import version as get_version
from .client import BBORClient


__version__ = get_version('bbor_client')
__all__ = [
    'BBORClient',
    '__version__',
]

