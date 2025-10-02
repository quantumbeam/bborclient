from pydantic import Field
from datetime import datetime, timedelta
from typing import Literal, Annotated, Optional, Union, Any
from .base import ClientModel, Link

class TrialNum(ClientModel):
    num: int
    trial: Link

class BestTrial(ClientModel):
    approach: Literal['lowestRwp']
    trial_num: int
    trial: Link
    Rwp: float
    GOF: float
    staled: bool = False

class Instrument(ClientModel):
    name: Optional[str] = None
    type: Literal['desktop', 'standing', 'beamline', None] = None
    catalog_id: Optional[str] = None
    catalog_name: Optional[str] = None
    beamline: Optional[str] = None
    facility: Optional[str] = None
    maker: Optional[str] = None
    attachment: list[str] = []
    tags: list[str] = []

class BeamSpec(ClientModel):
    type: Literal[*DIFFRACTION_BEAM_TYPES] # type: ignore
    structure: Literal['continuous', 'pulse']
    # source: Literal[*XRAY_SOURCES]|None = None # type: ignore
    #NOTE: Target element is not included in a gpx object
    wave_lengths: Union[list[float], float, None]

class DiffractionBase(ClientModel):
    # load_from_gpx: bool
    measurement_file: str
    instrument: Instrument
    type: str = Field(pattern=r'[PS][XN][CT]-(BB|DS)') #e.g. 'PXC-BB'
    sample_form: Literal[*DIFFRACTION_SAMPLE_TYPES] # type: ignore
    method: Literal[*DIFFRACTION_METHODS] # type: ignore
    geometry: Literal[*DIFFRACTION_GEOMETRIES] # type: ignore
    beam: BeamSpec
    bank: int
    azimuth: Optional[float] = None
    measurement_id: Any = None

class BraggBrentano(DiffractionBase):
    method: Literal['CW']
    geometry: Literal['Bragg-Brentano']
    gonio_radius: float

class DebyeScherrer(DiffractionBase):
    method: Literal['CW']
    geometry: Literal['Debye-Scherrer']
    gonio_radius: float

MonochromaticBeam = Annotated[Union[BraggBrentano,DebyeScherrer], Field(discriminator='geometry')]

class TimeOfFlight(DiffractionBase):
    method: Literal['TOF']
    geometry: Literal['Debye-Scherrer']
    flight_path: float
    two_theta: float

Diffraction = Annotated[Union[MonochromaticBeam,TimeOfFlight], Field(discriminator='method')]

class Phase(ClientModel):
    name: str
    space_group: str
    crystal_system: Literal[*CRYSTAL_SYSTEMS] # type: ignore
    formula: Optional[str] = None

class Sample(ClientModel):
    phases: list[Phase]
    sample_id: Any = None


class ResumableAttributes(ClientModel):
    BBOR_version: str
    completed: bool
    start_at: datetime
    time_to_complete: timedelta
    n_trials_total: int
    n_startup_trials: int
    python_version: str
    optuna_version: str
    gsas2_version: Union[str, list[str]]


class StudyResponse(ClientModel):
    id: str = Field(validation_alias='_id')
    status: Literal[*STUDY_STATUS] # type: ignore
    trials: list[TrialNum]
    name: str = Field(alias='study_name')
    user: Link
    group: Link
    resumables: list[ResumableAttributes]
    start_at: datetime #NOTE: Duplicated for searching the collection
    updated_at: datetime
    n_trials_total: int
    n_startup_trials: int
    random_seed: Union[int, Literal['random'], None]
    random_seed_fix: int
    sequence_version: Optional[str] = None
    sequence_version_fix: str
    sequence_kwargs: Optional[dict] = None
    num_sequence_steps: int = -1
    measurements: list[Diffraction]
    samples: list[Sample]
    path_in_obs: str
    best_trials: list[BestTrial] = Field(alias='best_trials')
    tags: list[str] = []
