from abc import ABC, abstractmethod
from typing import Union, Optional
from pathlib import Path
import io
from dataclasses import dataclass


@dataclass
class ParsedData:
    header: str
    twotheta: list[float]
    counts: list[float]


class ParserInterface(ABC):
    def __init__(
            self,
            filepath: Optional[Union[str,Path]] = None,
            filename: Optional[str] = None,
            filecontent: Optional[bytes] = None,
    ):
        # Populate path-related variables
        if filepath:
            filepath = Path(filepath)
            filename = filepath.name
            filecontent = filepath.read_bytes()
        
        assert filename is not None, 'Either filepath or filename must be provided.'
        assert filecontent is not None, 'Either filepath or filecontent must be provided.'

        # self._path = filepath.as_posix() #NOTE: Parser should not have file location info
        self._name = filename
        self._ext = filename.rsplit('.',1)[-1].lower()
        self._csvname = filename.rsplit('.',1)[0] + '.csv'

        # Parse the file and populate variables of measurement data
        data = self._parse(filecontent.decode('utf-8'))
        self._header = data.header
        self._twotheta = data.twotheta
        self._counts = data.counts


    @abstractmethod
    def _parse(self, content:str) -> ParsedData:...


    # @property
    # def path(self) -> str:
    #     return self._path
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


