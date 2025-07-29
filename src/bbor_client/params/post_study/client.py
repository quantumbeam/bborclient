import json
from pydantic import BaseModel, Field, model_validator, field_validator, FilePath, DirectoryPath
from typing import Annotated, Optional, Union, ClassVar
from pathlib import Path
import random
from .server import StudyNameConstraints, TrialNumbers, RandomSeedConstraints, DuplicateStudyControl, Tags, MeasurementConditions
from ...conf import MAX_RANDOM_SEED, MFILE_SUFFIXES, PRM_SUFFIXES, CIF_SUFFIXES

class StudyNameInput(BaseModel):
    '''
    Represents the input parameters for study_name.

    Specify either 'study_name' or 'study_name_base'.
    When 'study_name_base' is specified, the 'study_name' will be generated
    by appending the random seed number to the base name, e.g. study_name = study_name_base_s1234.

    Further validations are applied by limiting maximum length and usable characters.
    '''
    study_name: Optional[Annotated[str, StudyNameConstraints]] = None
    study_name_base: Optional[str] = Field(None, exclude=True)

    @model_validator(mode='after')
    def validate_exclusive_study_names(self):
        studyname_present = self.study_name is not None
        studynamebase_present = self.study_name_base is not None
        if studyname_present + studynamebase_present == 2:
            raise KeyError('Exclusive parameters are specified. Choose either study_name or study_name_base.')
        if studyname_present + studynamebase_present == 0:
            raise KeyError('Required parameter is missing. Specify either study_name or study_name_base.')
        return self

class TrialNumberInput(TrialNumbers):...

class RandomSeedInput(BaseModel):
    '''
    Represents the random seed number used in initial random search by optuna.

    If not specified, a random seed will be generated.
    '''
    random_seed: Optional[Annotated[int, RandomSeedConstraints]] = None

    @field_validator('random_seed', mode='after')
    def generate_random_seed(cls, random_seed):
        if random_seed is None:
            random_seed = random.randint(0, MAX_RANDOM_SEED-1)
            print(f'random_seed is generated as {random_seed}')
        return random_seed

class GPXFileInput(BaseModel):
    gpxfile: Optional[FilePath] = Field(None, exclude=True)

class MeasurementFileInput(BaseModel):
    measurementfile: Optional[FilePath] = Field(None, exclude=True)

class PRMFileInput(BaseModel):
    prm_filename: Optional[str] = None
    prmfile: Optional[FilePath] = Field(None, exclude=True)
    prm_file_list: ClassVar[list[str]] = [] # Dynamically populated at runtime
    overwrite_prmfile: bool = False

    @model_validator(mode='after')
    def exclusive_prmfile_prmfilename(self):
        prm_filename_present = self.prm_filename is not None
        prmfile_present = self.prmfile is not None
        if prm_filename_present + prmfile_present > 1:
            raise KeyError('Exclusive parameters specified. Choose either prm_filename or prmfile')
        return self
   
    @model_validator(mode='after')
    def populate_prm_filename(self):

        if self.prm_filename is None and self.prmfile is not None:
            filename = self.prmfile.name
            if filename in self.prm_file_list:
                pass
            self.prm_filename = self.prmfile.name
        return self
    
    @model_validator(mode='after')
    def func(self):
        if self.prm_filename is not None:
            if self.prm_filename in self.prm_file_list:
                pass
        return self

class CIFFileInput(BaseModel):

    ciffiles: Optional[Union[FilePath, list[FilePath]]] = Field(None, exclude=True)
    cif_file_list: ClassVar[list[str]] = [] # Dynamically populated at runtime

    @field_validator('ciffiles', mode='after')
    def ensure_ciffiles_list(cls, ciffiles):
        if isinstance(ciffiles, Path):
            return [ciffiles]
        else:
            return ciffiles

class Inputdir:
    inputdir: Optional[DirectoryPath] = Field(None, exclude=True)

class InputFilesInput(
    GPXFileInput,
    MeasurementFileInput,
    PRMFileInput,
    CIFFileInput,
    Inputdir,
):
    @model_validator(mode='after')
    def mutually_exclusive_parameters_with_inputdir(self):
        gpx_present = self.gpxfile is not None
        mfile_present = self.measurementfile is not None
        prm_present = self.prmfile is not None
        cif_present = self.prmfile is not None
        inputdir_present = self.inputdir is not None
        if inputdir_present:
            if any([gpx_present, mfile_present, prm_present, cif_present]):
                raise KeyError('Exclusive parameters specified. When specifying inputdir, gpxfile, measurementfile, prmfile, and ciffiles are not required.')
        return self
    
    @model_validator(mode='after')
    def load_files_from_dir(self):
        if self.inputdir is None:
            return self
        self.ciffiles = []
        for file in self.inputdir.iterdir():
            if not file.is_file():
                continue
            elif file.suffix.lower()=='.gpx':
                self.gpxfile = file
            elif file.suffix.lower() in MFILE_SUFFIXES:
                self.measurementfile = file
            elif file.suffix.lower() in PRM_SUFFIXES:
                self.prmfile = file
            elif file.suffix.lower() in CIF_SUFFIXES:
                self.ciffiles.append(file)
        return self

class SequenceInput(BaseModel):
    '''
    Specify a BBO-Rietveld sequence by either a sequence name or a sequence file.

    When specifying by name, you have to choose from the list which can be seen by client.sequence_list.
    
    '''
    sequence: str = 'latest'
    # sequence: Optional[str] = None
    # sequencefile: Optional[FilePath] = Field(None, exclude=True)
    sequence_args: Optional[dict] = None
    sequence_args_json: Optional[str] = None
    # overwrite: bool = Field(False, exclude=True)

    @model_validator(mode='after')
    def dump_sequence_args(self):
        if self.sequence_args_json is None and self.sequence_args is not None:
            self.sequence_args_json = json.dumps(self.sequence_args)
        return self


class PostStudyClientParams(
    StudyNameInput,
    TrialNumberInput,
    RandomSeedInput,
    InputFilesInput,
    SequenceInput,
    DuplicateStudyControl,
    Tags,
    MeasurementConditions,
):
    '''
    Represents the input parameters for users to post a new study to the BBOR API server.
    '''
    @model_validator(mode='after')
    def generate_study_name(self):
        if self.study_name is None:
            self.study_name = f'{self.study_name_base}_s{self.random_seed:04d}'
            print(f'study_name is generated as {self.study_name}')
        return self
