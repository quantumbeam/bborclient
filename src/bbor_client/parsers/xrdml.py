import xmltodict
import re
from .interface import ParserInterface, ParsedData


class Parser(ParserInterface):

    @classmethod
    def _remove_counts(cls, original: str) -> str:
        '''Removes counts strings and returns only header information as string.'''
        pattern = r'(?<=\<counts unit="counts"\>)[\d.\s\n]+(?=\</counts\>)'
        removed = re.sub(pattern, '', original)
        return removed


    def _parse(self, content: str) -> ParsedData:
        self._data = xmltodict.parse(content)
        header = self._remove_counts(content)

        scan_data = self._data['xrdMeasurements']['xrdMeasurement']['scan']
        data_points =  scan_data['dataPoints']
        count_data = data_points['counts']['#text']
        angle_data = data_points['positions']
        ttheta_data = next(d for d in angle_data if d['@axis']=='2Theta')

        # Extract histogram
        counts = list(map(float, count_data.split()))
        hist_length = len(counts)
        ttheta_start = float(ttheta_data['startPosition'])
        ttheta_end = float(ttheta_data['endPosition'])
        ttheta_step = (ttheta_end - ttheta_start) / (hist_length - 1)
        twotheta = [ttheta_start + i*ttheta_step for i in range(hist_length)]

        return ParsedData(
            header = header,
            twotheta = twotheta,
            counts = counts,
        )





