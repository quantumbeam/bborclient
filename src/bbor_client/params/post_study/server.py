import json
from pydantic import BaseModel, Field, StringConstraints, model_validator, field_validator, ConfigDict
from typing import Annotated, Optional, BinaryIO, ClassVar
from io import BufferedReader
from ...util import get_file_size_from_binaryio
from ...conf import MAX_STUDY_NAME_LENGTH, MIN_STUDY_NAME_LENGTH, MAX_N_TRIALS_TOTAL, DEFAULT_N_TRIALS_TOTAL, MAX_RANDOM_SEED, MAX_FILE_NAME_LENGTH, MAX_FILE_SIZE, MAX_MEAS_FILESIZE

StudyNameConstraints = StringConstraints(
    max_length=MAX_STUDY_NAME_LENGTH,
    min_length=MIN_STUDY_NAME_LENGTH,
    # pattern=r'^[^$\\\'"]+$', # Any characters allowed for now
)

TrialNumberConstraints = Field(
    gt = 0,
    lt = MAX_N_TRIALS_TOTAL,
)
RandomSeedConstraints = Field(
    ge = 0,
    lt = MAX_RANDOM_SEED,
)
FileNameConstraints = StringConstraints(
    max_length = MAX_FILE_NAME_LENGTH,
    min_length = 1,
    pattern=r'^[\w\-. \u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]+$',
    # Allow alphanumeric, underscore, hyphen, dot, space, and CJK characters
)

class StudyName(BaseModel):
    study_name: Annotated[str, StudyNameConstraints] = Field()

class TrialNumbers(BaseModel):
    '''
    Represents the total number of trials and the number of startup trials.
    '''
    n_trials_total: Annotated[int, TrialNumberConstraints] = DEFAULT_N_TRIALS_TOTAL
    n_startup_trials: Annotated[int, TrialNumberConstraints] # Additional validation below

    @model_validator(mode='after')
    def validate_n_startup_trials(self):
        if self.n_startup_trials > self.n_trials_total:
            raise ValueError(f'n_startup_trials should be smaller than or equal to n_trials_total')
        return self

class RandomSeed(BaseModel):
    '''
    Represents the random seed number used in initial random search by optuna.
    '''
    random_seed: Annotated[int, RandomSeedConstraints]

class GPXFile(BaseModel):
    gpx_filecontent: Optional[BinaryIO] = Field(None, exclude=True)
    gpx_filename: Optional[Annotated[str, FileNameConstraints]] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @field_validator('gpx_filecontent', mode='after')
    def validate_gpx_file_size(cls, binaryio):
        if binaryio is not None:
            size = get_file_size_from_binaryio(binaryio)
            if size > MAX_FILE_SIZE:
                raise ValueError(f'GPX file size exceeds maximum limit of {MAX_FILE_SIZE} MB')
        return binaryio

    @model_validator(mode='after')
    def check_gpx_file_filename_pair(self):
        file_present = self.gpx_filecontent is not None
        filename_present = self.gpx_filename is not None
        if file_present + filename_present == 1:
            raise KeyError(
                'Both gpx_file and gpx_filename should be set.'
            )
        return self

class MeasurementFile(BaseModel):
    measurement_filecontent: Optional[BufferedReader] = Field(None, exclude=True)
    measurement_filename: Optional[Annotated[str, FileNameConstraints]] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @field_validator('measurement_filecontent', mode='after')
    def validate_measurement_file_size(cls, binaryio):
        if binaryio is not None:
            size = get_file_size_from_binaryio(binaryio)
            if size > MAX_MEAS_FILESIZE:
                raise ValueError(f'Measurement file size exceeds maximum limit of {MAX_MEAS_FILESIZE} MB')
        return binaryio

    @model_validator(mode='after')
    def check_measurement_file_filename_pair(self):
        file_present = self.measurement_filecontent is not None
        filename_present = self.measurement_filename is not None
        if file_present + filename_present == 1:
            raise KeyError(
                'Both measurement_file and measurement_filename should be set.'
            )
        return self

class PRMFile(BaseModel):
    prm_filename: Optional[Annotated[str, FileNameConstraints]] = None
    prm_file_list: ClassVar[list[str]] = [] # Dynamically populated at runtime

    @field_validator('prm_filename', mode='after')
    def check_if_prm_file_exists_on_server(cls, filename):
        if filename is not None and filename not in cls.prm_file_list:
            raise ValueError(f'{filename} does not exist on the server. You need to upload it first.')
        return filename

class CIFFile(BaseModel):
    cif_filenames: Optional[list[Annotated[str, FileNameConstraints]]] = None
    cif_file_list: ClassVar[list[str]] = [] # Dynamically populated at runtime

    @field_validator('cif_filenames', mode='after')
    def check_if_cif_file_exists_on_server(cls, filenames):
        if filenames is None:
            return filenames
        for filename in filenames:
            if filename not in cls.cif_file_list:
                raise ValueError(f'{filename} does not exist on the server. You need to upload it first.')
        return filenames

class InputFiles(
    GPXFile,
    MeasurementFile,
    PRMFile,
    CIFFile,
):
    @model_validator(mode='after')
    def choose_either_gpx_or_measurement_file(self):
        gpxfile_present = self.gpx_filecontent is not None
        mfile_present = self.measurement_filecontent is not None
        if not (gpxfile_present + mfile_present == 1):
            raise ValueError(f'Specify either gpxfile or measurement_file')
        return self

    @model_validator(mode='after')
    def check_prmfile_ciffiles_requirements(self):
        mfile_present = self.measurement_filecontent is not None
        prm_present = self.prm_filename is not None
        cif_present = self.cif_filenames is not None
        if mfile_present:
            if not prm_present:
                raise KeyError('prm_file is required when measurement_file is specified.')
            if not cif_present:
                raise KeyError('cif_files is required when measurement_file is specified.')
        else: #gpx_file specified
            if prm_present:
                raise KeyError('Exclusive parameters set. prm_file not required when gpx_file is specified')
            if cif_present:
                raise KeyError('Exclusive parameters set. cif_files not required when gpx_file is specified')
        return self


class Sequence(BaseModel):
    sequence: str
    # sequence_args_json: Optional[str] = Field(None)
    sequence_list: ClassVar[list[str]] = [] # Dynamically populated at runtime

    @field_validator('sequence', mode='after')
    def check_if_sequence_in_list(cls, sequence):
        if sequence not in cls.sequence_list:
            raise ValueError(f'{sequence} is not a valid sequence. Please choose from the available sequences.')
        return sequence
    
    # @field_validator('sequence_args_json', mode='after')
    # def validate_sequence_args_jsonable(cls, sequence_args_json):
    #     if sequence_args_json is None:
    #         return sequence_args_json
    #     try:
    #         _ = json.loads(sequence_args_json)
    #     except TypeError:
    #         raise TypeError('sequence_args_json must be a json string')
    #     return sequence_args_json

class BackgroundFile(BaseModel):
    # Not yet implemented
    pass

class DuplicateStudyControl(BaseModel):
    initialize_study: bool = False

class Tags(BaseModel):
    tags: list[str] = []

class MeasurementConditions(BaseModel):
    pass



class PostStudyServerParams(
    StudyName,
    TrialNumbers,
    RandomSeed,
    InputFiles,
    DuplicateStudyControl,
    Sequence,
    Tags,
    MeasurementConditions,
):
    '''
    Represents the parameters of an HTTP request to post a new study to the BBOR API server.
    '''


