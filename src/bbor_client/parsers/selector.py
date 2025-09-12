import importlib
from typing import Type
from .interface import ParserInterface

def selector(
        filename: str,
) -> Type[ParserInterface]:
    extension = filename.lower().split('.')[-1]
    module = importlib.import_module(f'bbor_client.parsers.{extension}')
    return module.Parser



