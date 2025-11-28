import io
import pandas as pd
from .interface import ParserInterface, ParsedData


class Parser(ParserInterface):
    @classmethod
    def _validate(cls, df):
        if (df.dtypes==float).all() is False:
            raise ValueError


    def _parse(self, content:str) -> ParsedData:
        df = pd.read_csv(io.StringIO(content), sep=' ', header=None)
        header = ''
        twotheta = df[0]
        counts = df[1]
        self._validate(df)
        return ParsedData(
            header = header,
            twotheta = twotheta.tolist(),
            counts = counts.tolist(),
        )
