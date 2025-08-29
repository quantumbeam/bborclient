from abc import ABC, abstractmethod
from typing import Union
from pathlib import Path
import io
from dataclasses import dataclass


@dataclass
class ParsedData:
    header: str
    twotheta: list[float]
    counts: list[float]


class ParserInterface(ABC):
    def __init__(self, filepath: Union[str,Path]):
        # Populate path-related variables
        if isinstance(filepath, str):
            filepath = Path(filepath)
        self._path = filepath.as_posix()
        self._name = filepath.name
        self._csvname = filepath.with_suffix('.csv').name
        self._ext = filepath.suffix

        # Parse the file and populate variables of measurement data
        data = self._parse(filepath.as_posix())
        self._header = data.header
        self._twotheta = data.twotheta
        self._counts = data.counts


    @abstractmethod
    def _parse(self, filepath:str) -> ParsedData:...


    @property
    def path(self) -> str:
        return self._path
    @property
    def name(self) -> str:
        return self._name
    @property
    def csvname(self) -> str:
        return self._csvname
    @property
    def ext(self) -> str:
        return self._ext
    @property
    def header(self) -> str:
        return self._header
    @property
    def twotheta(self) -> list[float]:
        return self._twotheta
    @property
    def counts(self) -> list[float]:
        return self._counts

    def _to_csv_bytesio(self) -> io.BufferedReader:
        '''Converts histogram data to CSV format and returns as an IO object for the API upload.'''
        output = io.StringIO()
        # output.write("2Theta,Counts\n") # GSASII does not require title line
        for ttheta, count in zip(self.twotheta, self.counts):
            output.write(f'{ttheta},{count}\n')
        output.seek(0)
        return io.BufferedReader(
            io.BytesIO(output.read().encode('utf-8'))
        )


