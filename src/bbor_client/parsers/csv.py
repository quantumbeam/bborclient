import io, re
import pandas as pd
from .interface import ParserInterface, ParsedData

# Text pattern for the main count data part
SEP = r'[,\s]'
NUMERIC = r'[\+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][\+\-]?\d+)?'
DPATTERN = re.compile(rf'^{SEP}*{NUMERIC}(?:({SEP}+){NUMERIC})+{SEP}*$')
# Can match '123     -.456\t+7e-8,     .9'
# Not match '123, abc' Requires all columns to be numeric
# Not match '123' Requires at least two numeric columns
# Not match '123,' Blanks NOT allowed with two columns
# Can match '123,, 456' Blanks ARE allowed with more than three columns
# match.group(1) returns the final seperator characters of the line


# Minimum number of lines that must match the pattern to detect the start of the main part
MIN_MATCHING_LINES = 10

# Maximum number of lines to read in detecting the start of the main part
MAX_READ_LINES = 200 # 

class Parser(ParserInterface):

    @classmethod
    def _validate(cls, df: pd.DataFrame):
        if (df.dtypes==float).all() is False:
            raise ValueError

    @classmethod
    def _sep_selector(cls, sep_string: str) -> str:
        if ',' in sep_string:
            sep = ','
        elif '\t' in sep_string:
            sep = r'\t',
        elif sep_string.isspace():
            sep = r'\s+'
        else:
            sep = sep_string
        return sep # type: ignore

    @classmethod
    def _detect_header_separator(cls, content: str) -> tuple[str, int, str]:
        count_dlines = 0
        for i,line in enumerate(content.splitlines()):
            if match_ := DPATTERN.match(line):
                if count_dlines >= MIN_MATCHING_LINES:
                    header_count = i - count_dlines
                    header = '\n'.join(content.splitlines()[:header_count])
                    sep = match_.group(1)
                    return header, header_count, sep
                count_dlines += 1
            elif i < MAX_READ_LINES:
                continue
            else:
                raise ValueError('Cannot parse the file')
        raise ValueError('Maybe measurement file too short?')

    def _parse(self, content: str) -> ParsedData:
        header, skiprows, sep_string = self._detect_header_separator(content)
        sep = self._sep_selector(sep_string)
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







