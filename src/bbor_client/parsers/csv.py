import io, re
import pandas as pd
from .interface import ParserInterface, ParsedData

SEP = r'[,\s]'
NUMERIC = r'[\+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][\+\-]?\d+)?'
DPATTERN = re.compile(rf'^{SEP}*{NUMERIC}(?:({SEP}+){NUMERIC})+{SEP}*$')
# Can match '123     -.456\t+7e-8,     .9'
# Not match '123, abc' Requires all columns to be numeric
# Not match '123' Requires at least two numeric columns
SUFFICIENT_LINE_COUNT = 10
TOLERANCE_LINE_COUNT = 200

class Parser(ParserInterface):

    @classmethod
    def _validate(cls, df: pd.DataFrame):
        if (df.dtypes==float).all() is False:
            raise ValueError

    @classmethod
    def _detect_header_separator(cls, content: str) -> tuple[str, int, str]: # type: ignore
        count_dlines = 0
        for i,line in enumerate(content.splitlines()):
            if match_ := DPATTERN.match(line):
                if count_dlines >= SUFFICIENT_LINE_COUNT:
                    header_count = i - count_dlines
                    header = '\n'.join(content.splitlines()[:header_count])
                    sep = match_.group(1)
                    return header, header_count, sep
                count_dlines += 1
            elif i < TOLERANCE_LINE_COUNT:
                continue
            else:
                raise ValueError('Cannot parse the file')

    def _parse(self, content: str) -> ParsedData:

        header, skiprows, sep_string = self._detect_header_separator(content)

        if ',' in sep_string:
            sep = ','
        elif '\t' in sep_string:
            sep = '\t',
        elif sep_string.isspace():
            sep = r'\s+'
        else:
            sep = sep_string
        df = pd.read_csv(
            io.StringIO(content),
            sep = sep, # type: ignore
            skiprows=skiprows,
            header=None,
            usecols = [0,1],
        )

        self._validate(df)

        return ParsedData(
            header = header,
            twotheta = df.iloc[:,0].tolist(),
            counts = df.iloc[:,1].tolist(),
        )







