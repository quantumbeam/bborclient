'''Validation rules of the parameters sent to the API when posting a study.

Each test states which input is accepted, and for a rejected input, which
parameter is reported. A rule broken by the combination of several parameters
is reported for the whole model (an empty location).

The rules for the GPX file aren't covered: no client sends its contents yet.
'''
import io
import pytest
from pydantic import ValidationError
from bbor_client.conf import (
    MAX_STUDY_NAME_LENGTH, MAX_N_TRIALS_TOTAL, MAX_RANDOM_SEED,
    MAX_FILE_NAME_LENGTH, MAX_MEAS_FILESIZE,
)
from bbor_client.params.post_study.server import (
    StudyName, TrialNumbers, RandomSeed, MeasurementFile, InputFiles,
)


def error_locations(excinfo: pytest.ExceptionInfo[ValidationError]) -> list[tuple]:
    return [error['loc'] for error in excinfo.value.errors()]


def file_of_size(size: int) -> io.BufferedReader:
    return io.BufferedReader(io.BytesIO(b'0' * size))


@pytest.fixture
def files_on_server(monkeypatch):
    '''The PRM and CIF files that exist on the server for the user's group.'''
    monkeypatch.setattr(InputFiles, 'prm_file_list', ['sample.instprm'])
    monkeypatch.setattr(InputFiles, 'cif_file_list', ['phase1.cif', 'phase2.cif'])


class TestStudyName:
    @pytest.mark.parametrize('study_name', [
        'a',
        'Sample 1 データ',
        'a' * MAX_STUDY_NAME_LENGTH,
    ])
    def test_accepted(self, study_name):
        StudyName(study_name=study_name)

    @pytest.mark.parametrize('study_name', [
        '',
        'a' * (MAX_STUDY_NAME_LENGTH + 1),
    ])
    def test_rejected(self, study_name):
        with pytest.raises(ValidationError) as excinfo:
            StudyName(study_name=study_name)
        assert error_locations(excinfo) == [('study_name',)]


class TestTrialNumbers:
    @pytest.mark.parametrize('n_trials_total, n_startup_trials', [
        (200, 10),
        (1, 1),
        (MAX_N_TRIALS_TOTAL - 1, MAX_N_TRIALS_TOTAL - 1),
    ])
    def test_accepted(self, n_trials_total, n_startup_trials):
        TrialNumbers(n_trials_total=n_trials_total, n_startup_trials=n_startup_trials)

    @pytest.mark.parametrize('n_trials_total, n_startup_trials, location', [
        (0, 1, ('n_trials_total',)),
        (MAX_N_TRIALS_TOTAL, 1, ('n_trials_total',)),
        (200, 0, ('n_startup_trials',)),
        (200, 201, ()),
    ])
    def test_rejected(self, n_trials_total, n_startup_trials, location):
        with pytest.raises(ValidationError) as excinfo:
            TrialNumbers(n_trials_total=n_trials_total, n_startup_trials=n_startup_trials)
        assert error_locations(excinfo) == [location]

    def test_n_startup_trials_is_required(self):
        with pytest.raises(ValidationError) as excinfo:
            TrialNumbers(n_trials_total=200)
        assert error_locations(excinfo) == [('n_startup_trials',)]


class TestRandomSeed:
    @pytest.mark.parametrize('random_seed', [0, MAX_RANDOM_SEED - 1])
    def test_accepted(self, random_seed):
        RandomSeed(random_seed=random_seed)

    @pytest.mark.parametrize('random_seed', [-1, MAX_RANDOM_SEED])
    def test_rejected(self, random_seed):
        with pytest.raises(ValidationError) as excinfo:
            RandomSeed(random_seed=random_seed)
        assert error_locations(excinfo) == [('random_seed',)]


class TestMeasurementFile:
    @pytest.mark.parametrize('filename', [
        'sample.csv',
        'sample_1-2 a.csv',
        '試料_データ.xrdml',
        'a' * MAX_FILE_NAME_LENGTH,
    ])
    def test_accepted_filenames(self, filename):
        MeasurementFile(measurement_filecontent=file_of_size(10), measurement_filename=filename)

    @pytest.mark.parametrize('filename', [
        '',
        'dir/sample.csv',
        'sample;.csv',
        'a' * (MAX_FILE_NAME_LENGTH + 1),
    ])
    def test_rejected_filenames(self, filename):
        with pytest.raises(ValidationError) as excinfo:
            MeasurementFile(measurement_filecontent=file_of_size(10), measurement_filename=filename)
        assert error_locations(excinfo) == [('measurement_filename',)]

    def test_largest_file_accepted(self):
        MeasurementFile(
            measurement_filecontent=file_of_size(MAX_MEAS_FILESIZE),
            measurement_filename='sample.csv',
        )

    def test_too_large_file_rejected(self):
        with pytest.raises(ValidationError) as excinfo:
            MeasurementFile(
                measurement_filecontent=file_of_size(MAX_MEAS_FILESIZE + 1),
                measurement_filename='sample.csv',
            )
        assert error_locations(excinfo) == [('measurement_filecontent',)]

    def test_file_without_filename_rejected(self):
        with pytest.raises(ValidationError) as excinfo:
            MeasurementFile(measurement_filecontent=file_of_size(10))
        assert error_locations(excinfo) == [()]

    def test_filename_without_file_rejected(self):
        with pytest.raises(ValidationError) as excinfo:
            MeasurementFile(measurement_filename='sample.csv')
        assert error_locations(excinfo) == [()]


@pytest.mark.usefixtures('files_on_server')
class TestInputFiles:
    def test_measurement_with_prm_and_cifs_accepted(self):
        InputFiles(
            measurement_filecontent=file_of_size(10),
            measurement_filename='sample.csv',
            prm_filename='sample.instprm',
            cif_filenames=['phase1.cif', 'phase2.cif'],
        )

    def test_no_measurement_rejected(self):
        with pytest.raises(ValidationError) as excinfo:
            InputFiles(prm_filename='sample.instprm', cif_filenames=['phase1.cif'])
        assert error_locations(excinfo) == [()]

    @pytest.mark.parametrize('missing', ['prm_filename', 'cif_filenames'])
    def test_measurement_without_prm_or_cifs_rejected(self, missing):
        params = dict(
            measurement_filecontent=file_of_size(10),
            measurement_filename='sample.csv',
            prm_filename='sample.instprm',
            cif_filenames=['phase1.cif'],
        )
        del params[missing]
        with pytest.raises(ValidationError) as excinfo:
            InputFiles(**params)
        assert error_locations(excinfo) == [()]
