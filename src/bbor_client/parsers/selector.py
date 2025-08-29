import importlib
from typing import Type
from .interface import ParserInterface

def selector(
        extension: str
) -> Type[ParserInterface]:

    module = importlib.import_module(f'bbor_client.parsers.{extension.lower().lstrip(".")}')
    return module.Parser



