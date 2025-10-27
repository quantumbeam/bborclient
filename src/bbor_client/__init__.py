import os
from .client import BBORClient

#INFO: tomllib becomes standard with Python>3.11.
# bbor_client requires 3.9 or over, so __version__ reads pyproject.toml using importlib.
# But the BBOR server cannot importlib.meta for reading the version value
# because it does not install the client as a package but setting PYTHONPATH.
# Therefore, tomllib is used to directly read pyproject.toml

try:
    import tomllib
    pyproject_path = os.path.join(os.path.dirname(__file__), '../..', 'pyproject.toml')
    with open(pyproject_path, 'rb') as f:
        data = tomllib.load(f)
    __version__ = data['project']['version']
except ModuleNotFoundError:
    from importlib.metadata import version as _get_version
    __version__ = _get_version(__package__ or 'bbor_client')


__all__ = [
    'BBORClient',
    '__version__',
]

