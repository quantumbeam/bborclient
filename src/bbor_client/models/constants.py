from typing import get_args
from .study import Study, BeamSpec, DiffractionBase, Phase
from .trial import PolynomialBackground

STUDY_STATUS:tuple = get_args(Study.model_fields['status'].annotation)

DIFFRACTION_BEAM_TYPES:tuple = get_args(BeamSpec.model_fields['type'].annotation)
DIFFRACTION_BEAM_STRUCTURES:tuple = get_args(BeamSpec.model_fields['structure'].annotation)
DIFFRACTION_SAMPLE_TYPES:tuple = get_args(DiffractionBase.model_fields['sample_form'].annotation)
DIFFRACTION_METHODS:tuple = get_args(DiffractionBase.model_fields['method'].annotation)
DIFFRACTION_GEOMETRIES:tuple = get_args(DiffractionBase.model_fields['geometry'].annotation)

GSASII_BG_FUNCTIONS:tuple = get_args(
    PolynomialBackground.model_fields['func'].annotation
)

CRYSTAL_SYSTEMS:tuple = get_args(Phase.model_fields['crystal_system'].annotation)

