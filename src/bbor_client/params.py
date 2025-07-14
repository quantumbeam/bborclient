from pydantic import BaseModel, Field, StringConstraints, model_validator, field_validator, DirectoryPath, FilePath
from typing import Annotated, Optional, BinaryIO
import random
from .conf import MAX_STUDY_NAME_LENGTH, MIN_STUDY_NAME_LENGTH, DEFAULT_N_TRIALS_TOTAL, MAX_N_TRIALS_TOTAL, MAX_RANDOM_SEED


StudyNameConstraints = StringConstraints(
    max_length=MAX_STUDY_NAME_LENGTH,
    min_length=MIN_STUDY_NAME_LENGTH,
    # pattern=r'^[^$\\\'"]+$', # Any characters allowed for now
)
StudyNameBaseConstraints = StringConstraints(
    max_length=MAX_STUDY_NAME_LENGTH-6,
    min_length=MIN_STUDY_NAME_LENGTH,
    # pattern=r'^[^$\\\'"]+$', # Any characters allowed for now
)

class StudyName(BaseModel):
    study_name: Annotated[str, StudyNameConstraints] = Field()

class StudyNameInput(BaseModel):
    '''
    Represents the input parameters for study_name.

    Specify either 'study_name' or 'study_name_base'.
    When 'study_name_base' is specified, the 'study_name' will be generated
    by appending the random seed number to the base name, e.g. study_name = study_name_base_s1234.
    '''
    study_name: Optional[Annotated[str, StudyNameConstraints]] = Field()
    study_name_base: Optional[Annotated[str, StudyNameBaseConstraints]] = Field()

    @model_validator(mode='after')
    def validate_exclusive_study_names(self):
        has_studyname = self.study_name is not None
        has_studynamebase = self.study_name_base is not None
        if all([has_studyname, has_studynamebase]):
            raise KeyError('Exclusive parameters are specified. Choose either study_name or study_name_base.')
        elif has_studyname==False and has_studynamebase==False:
            raise KeyError('Required parameter is missing. Specify either study_name or study_name_base.')
        return self

class TrialNumbers(BaseModel):
    '''
    Represents the total number of trials and the number of startup trials.
    '''
    n_trials_total: Annotated[int, Field(gt=0, lt=MAX_N_TRIALS_TOTAL)] = DEFAULT_N_TRIALS_TOTAL
    n_startup_trials: Optional[int] = None # validated below

    @model_validator(mode='after')
    def validate_n_startup_trials(self):
        if self.n_startup_trials is None:
            pass
        elif self.n_startup_trials < 0:
            raise ValueError(f'n_startup_trials should be greater than or equal to 0')
        elif self.n_startup_trials > self.n_trials_total:
            raise ValueError(f'self.n_startup_trials should be smaller than or equal to n_trials_total')
        return self

RandomSeedConstraints = Field(
    ge = 0,
    lt = MAX_RANDOM_SEED,
)

class RandomSeed(BaseModel):
    random_seed: Annotated[int, RandomSeedConstraints]

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

class InputFiles(BaseModel):
    '''
    Validates file inputs.

    1. gpxfile and gpxfile_name.
    2. prmfile, prmfile_name, mfile, mfile_name, ciffiles, ciffile_names
    3. prmfile_name, mfile, mfile_name, ciffile_names

    '''
    gpxfile: Optional[BinaryIO] = Field(None, exclude=True)
    gpxfile_name: Optional[str] = Field(None, exclude=True)
    prmfile: Optional[BinaryIO] = Field(None, exclude=True)
    prmfile_name: Optional[str] = Field(None, exclude=True)
    mfile: Optional[BinaryIO] = Field(None, exclude=True)
    mfile_name: Optional[str] = Field(None, exclude=True)
    ciffiles: Optional[list[BinaryIO]] = Field(None, exclude=True)
    ciffile_names: Optional[list[str]] = Field(None, exclude=True)

    @field_validator('gpxfile_name', mode='after')
    def validate_gpxfile_name(cls, gpxfile_name:str):
        if gpxfile_name is None:
            return None
        elif gpxfile_name.lower().endswith('.gpx'):
            return gpxfile_name
        else:
            raise ValueError(f'{gpxfile_name=} should be suffixed by ".gpx"')
    
    @field_validator('prmfile_name', mode='after')
    def validate_prmfile_name(cls, prmfile_name:str):
        if prmfile_name is None:
            return None
        elif prmfile_name.lower().endswith('.gpx'):
            return prmfile_name
        else:
            raise ValueError(f'{prmfile_name=} should be suffixed by ".gpx"')
    



    @model_validator(mode='after')
    def validate_exclusive_input_files(self):
        has_gpxfile = self.gpxfile is not None
        has_gpxfile_name = self.gpxfile_name is not None
        has_prmfile = self.prmfile is not None
        has_prmfile_name = self.prmfile_name is not None
        has_mfile = self.mfile is not None
        has_mfile_name = self.mfile_name is not None
        has_ciffiles = self.ciffiles is not None
        has_ciffile_names = self.ciffile_names is not None

        if has_gpxfile and has_gpxfile_name:
            if any((has_prmfile, has_prmfile_name, has_mfile, has_mfile_name, has_ciffiles, has_ciffile_names)):
                raise KeyError('Exclusive parameters are specified. Choose either (gpxfile and gpxfile_name) or (prmfile, prmfile_name, mfile, mfile_name, ciffiels, and ciffile_names).')
        elif has_gpxfile or has_gpxfile_name:
            raise KeyError('Required parameter is missing. Specify both gpxfile and gpxfile_name.')
        else:
            if not has_prmfile_name:
                raise KeyError('Required parameter is missing. Specify prmfile_name.')
            if not has_ciffile_names:
                raise KeyError('Required parameter is missing. Specify ciffile_names.')
            if not has_mfile:
                raise KeyError('Required parameter is missing. Specify mfile.')
            if not has_mfile_name:
                raise KeyError('Required parameter is missing. Specify mfile_name.')

        return self

class InputFilesInput(BaseModel):
    '''
    Represents the input files for the BBOR API server.
    The input files can be specified in three ways:
    1. inputdir: a directory containing all the input files
    2. gpxfile: a GPX file
    3. prmfile, mfile, ciffiles: a set of the (prmfile, mfile, ciffiles)
    '''
    inputdir: Optional[DirectoryPath] = Field(None, exclude=True)
    gpxfile: Optional[FilePath] = Field(None)
    prmfile: Optional[FilePath] = Field(None)
    mfile: Optional[FilePath] = Field(None)
    ciffiles: Optional[list[FilePath]] = Field(None)


    @model_validator(mode='after')
    def validate_exclusive_input_parameters(self):
        has_inputdir = self.inputdir is not None
        has_gpx = self.gpxfile is not None
        has_prm = self.prmfile is not None
        has_mdata = self.mfile is not None
        has_cifs = self.ciffiles is not None
        has_inputsuite = all([has_prm, has_mdata, has_cifs])
        all_inputs = ['inputdir', 'gpxfile', 'prmfile', 'mfile', 'ciffiles']
        if resume_study:
            if sum([has_inputdir, has_gpx, has_inputsuite])>0:
                raise KeyError(f'Exclusive arguments are specified. When resume_study is True, none of {all_inputs} can be specified.')
            else:
                return self
        else:
            if sum([has_inputdir, has_gpx, has_inputsuite])==0:
                raise KeyError('Required argument is missing. Specify either inputdir, gpx, or a set of the (prmfile, mfile, ciffiles).')
            elif sum([has_inputdir, has_gpx, has_inputsuite]) > 1:
                raise KeyError('Exclusive arguments are specified. Choose either inputdir, gpx, or a set of the (prmfile, mfile, ciffiles).')
            return self

    @field_validator('gpxfile')
    def validate_gpx(cls, gpxfile:FilePath|None):
        if gpxfile is None:
            return None
        if gpxfile.suffix.lower()=='.gpx':
            return gpxfile
        else:
            raise ValueError(f'{gpxfile=} should be suffixed by ".gpx"')

    @field_validator('prmfile')
    def validate_instprm(cls, prmfile:FilePath|None):
        if prmfile is None:
            return None
        if prmfile.suffix.lower() in ('.prm', '.instprm'):
            return prmfile
        else:
            raise ValueError(f'{prmfile=} should be suffixed by either ".prm" or "instprm"')

    @field_validator('ciffiles')
    def validate_cifs(cls, ciffiles:list[FilePath]|None):
        if ciffiles is None:
            return None
        for cif in ciffiles:
            if not cif.suffix.lower()=='.cif':
                raise ValueError(f'All of {ciffiles=} should be suffixed by ".cif"')
        return ciffiles

    @field_validator('mfile')
    def validate_measurement_data_file(cls, mfile:FilePath|None):
        if mfile is None:
            return None
        suffixes = ['.csv']
        if mfile.suffix.lower() in suffixes:
            return mfile
        else:
            raise ValueError(f'{mfile=} should be suffixed by either {" or".join(suffixes)}')

    @field_validator('gpxfile', 'prmfile', 'ciffiles', 'mfile')
    def validate_filesize(cls, file):
        if file in ['gpxfile','mfile']:
            max_file_size = MAX_MEAS_FILESIZE
        else:
            max_file_size = MAX_FILE_SIZE
        if isinstance(file, Path):
            filelist = [file]
        elif isinstance(file, list):
            filelist = file
        else:
            raise TypeError(f'{file=} should be a Path or a list of Paths')
        assert isinstance(file, list)
        for f in filelist:
            size = f.stat().st_size
            if size > max_file_size:
                raise ValueError(f'The file {f.name} is {f.stat().st_size/1024/1024:.1f} MB and should not exceed {max_file_size/1024/1024:.0f} MB')
        return file

class Sequence(BaseModel):
    pass

class SequenceInput(BaseModel):
    pass

class BackgroundFile(BaseModel):
    pass

class BackgroundFileInput(BaseModel):
    pass

class SaveInputFiles(BaseModel):
    save_prmfile_on_server: bool = False
    save_ciffiles_on_server: bool = False
    save_sequencefile_on_server: bool = False

class StudyDuplicationControl(BaseModel):
    pass

class Tags(BaseModel):
    pass

class MeasurementConditions(BaseModel):
    pass



class ParamsUserTask(
    StudyNameInput,
    TrialNumbers,
    RandomSeedInput,
    InputFiles,
    SaveInputFiles,
):
    '''
    Represents the input parameters for users to post a new study to the BBOR API server.
    '''
    @model_validator(mode='after')
    def generate_study_name(self):
        if self.study_name is None and self.study_name_base is not None and self.random_seed is not None:
            self.study_name = f'{self.study_name_base}_s{self.random_seed:04d}'
            print(f'study_name is generated as {self.study_name}')
        return self


class ParamsClientTask(
    StudyName,
    TrialNumbers,
    RandomSeed,
    InputFilesInput,
    SaveInputFiles,
):
    '''
    Represents the parameters of an HTTP request to post a new study to the BBOR API server.
    '''






