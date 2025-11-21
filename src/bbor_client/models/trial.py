from pydantic import BaseModel, Field, model_validator, conlist
from datetime import datetime, timedelta
from typing import Literal, Annotated, Optional, Union
# from bborclient.util import ClientModel, Link
# from bborclient.models.base import ClientModel, Link
from .base import ClientModel, Link
# from bborconstants import GSASII_BG_FUNCTIONS


class ConstantInt(ClientModel):
    value: int

class ConstantFloat(ClientModel):
    value: float
    unit: Optional[str] = None

class ErrorPropergatedFloat(ConstantFloat):
    sig: float

class RefinableFloat(ErrorPropergatedFloat):
    refine: bool = False
    sig: Optional[float] = None

class ConstrainableFloat(RefinableFloat):
    is_constrained: bool = False

class RefinableFloatList(ClientModel):
    values: list[float]
    # sigs: list[float] = [] #INFO: modified because sigs are ofter nulls
    sigs: list[Union[float,None]] = []
    refine: bool = False

    @model_validator(mode='after')
    def validate_list_length(self):
        values = self.values
        sigs = self.sigs
        if len(sigs)==0:
            return self
        elif len(values) != len(sigs):
            raise ValueError(f'The values and sigs should be equal in length. {values=}, {sigs=}')
        else:
            return self

class MillerIndex(ClientModel):
    hkl: conlist(int, min_length=3, max_length=3) # type: ignore



class SampleParametersBase(ClientModel):
    scale: RefinableFloat = Field(
        # serialization_alias='Scale',
        alias='Scale',
    )
    
class SampleParametersDebyeScherrer(SampleParametersBase):
    '''Parameters used commonly for all the Debye-Scherrer geometries'''

    absorption: RefinableFloat = Field(
        # serialization_alias='Absorption',
        alias='Absorption',
    )
    r'''
    Absorption (attenuation or transimission) correction factor.  
    This parameter assumes a cylindrical sample form and is therefore only valid for the Debye-Scherrer geometry.  
    In GSAS-II, a numerically approximated formula is used.  
    For the exact expression, refer to \[1\] or \[2\].
    Analytical formulations can be found in \[3\] or \[4\].  
    The refined parameter is $\mu R$ for $2\theta$-scan measurements and $\mu R/\lambda$ for TOF measurements,  
    where $\mu$ is the effective linear absorption coefficient, $R$ is the capillary radius.  
    $\lambda$ is the wavelength, derived from $\lambda = \mathrm{h}t/\mathrm{mL}$,  
    where $t$ is the time-of-flight, $\mathrm{L}$ is the flight path, $\mathrm{h}$ is Planck's constant, and $\mathrm{m}$ is the neutron mass.  
    \[1\] N. N. Lobanov and L. Alte da Veiga, 6th European Powder Diffraction Conference, 22-25 August 1998, Abstract P12-16.  
    \[2\] [Function 'Absorb' in GSASIIpwd.py of the GSAS-II code](https://github.com/AdvancedPhotonSource/GSAS-II/blob/a741546c792d9844d581732e735c0668061b7ffa/GSASII/GSASIIpwd.py#L155)  
    \[3\] E. N. Maslen, *International Tables for Crystallography*, Vol. C, 1st Edition, ch. 6.3: X-ray absorption (2006).  
    \[4\] [T. Ida, *J. Appl. Cryst.* **43**, 1124 (2010)](https://doi.org/10.1107/S0021889810021199)
    '''

class SampleParametersDebyeScherrerTOF(SampleParametersDebyeScherrer):
    '''Parameters used only for the Time-of-flight method'''
    type: Literal['TOF'] = 'TOF'

class SampleParametersDebyeScherrerCW(SampleParametersDebyeScherrer):
    '''Parameters used for the constant wave length Debye-Scherrer geometries'''
    type: Literal['DS'] = 'DS'

    displaceX: RefinableFloat = Field(
        # serialization_alias='DisplaceX',
        alias='DisplaceX',
    )
    r'''
    Peak shift due to sample displacement  .  
    The correction is give by  
    $\displaystyle
    \Delta 2\theta = -\frac{360}{2\pi \mathrm{R_g}}(\mathrm{s_x}\cos 2\theta + \mathrm{s_y}\sin 2\theta))
    $,  
    where $\mathrm{s_x}$ and $\mathrm{s_y}$ are the sample displacements in mm  
    perpendicular and parallel to the incident beam direction, respectively,  
    and $\mathrm{R_g}$ is the goniometer radius in mm.  
      
    R. B. Von Dreele, *International Tables for Crystallography*, Vol. H, 1st Edition, ch. 3.3: Powder diffraction peak profiles (2019).
    '''

    displaceY: RefinableFloat = Field(
        # serialization_alias='DisplaceY',
        alias='DisplaceY',
    )
    r'''
    Peak shift due to sample displacement  .  
    The correction is give by  
    $\displaystyle
    \Delta 2\theta = -\frac{360}{2\pi \mathrm{R_g}}(\mathrm{s_x}\cos 2\theta + \mathrm{s_y}\sin 2\theta))
    $,  
    where $\mathrm{s_x}$ and $\mathrm{s_y}$ are the sample displacements in mm  
    perpendicular and parallel to the incident beam direction, respectively,  
    and $\mathrm{R_g}$ is the goniometer radius in mm.  
      
    R. B. Von Dreele, *International Tables for Crystallography*, Vol. H, 1st Edition, ch. 3.3: Powder diffraction peak profiles (2019).
    '''


class SampleParametersBraggBrentano(SampleParametersBase):
    type: Literal['BB'] = 'BB'

    shift: RefinableFloat = Field(
        # serialization_alias='Shift',
        alias='Shift',
    )
    r'''
    Peak shift due to sample displacement from the center of the diffractometer circle.  
    The correction is given by  
    $\displaystyle
    \Delta 2\theta = - \frac{\mathrm{s}}{1000}\frac{2\cos\theta}{\mathrm{R_g}}\frac{360}{2\pi}
    $,  
    where $\mathrm{s}$ is the sample displacement in $\mu$m (positive when displaced away from the focusing circle),  
    and $\mathrm{R_g}$ is the goniometer radius in mm.  
    '''

    transparency: RefinableFloat = Field(
        # serialization_alias='Transparency',
        alias='Shift',
    )
    r'''
    Peak shift caused by penetration of the beam into the sample.  
    The correction is given by  
    $\displaystyle
    \Delta 2\theta = - \frac{1}{10\mu}\frac{\sin 2\theta}{2\mathrm{R_g}}\frac{360}{2\pi}
    $,  
    where $1/\mu$ is the refinement parameter, *transparency*,  
    $\mu$ is the effective linear absorption coefficient in cm$^{-1}$,  
    and $\mathrm{R_g}$ is the goniometer radius in mm.
    '''

    surf_roughA: RefinableFloat = Field(
        # serialization_alias='SurfRoughA',
        alias='SurfRoughA',
    )
    r'''
    Surface roughness correction for the intensity.  
    The factor is given by  
    $[\mathrm{A} + (1-\mathrm{A})\exp(-\mathrm{B}/\sin\theta)] / \mathrm{C}$,  
    where $\mathrm{C} = \mathrm{A} + (1-\mathrm{A})\exp(-\mathrm{B})$ is the normalization factor.  
    [P. Suortti, *J. Appl. Cryst.* **5**, 325 (1972)](https://doi.org/10.1107/S0021889872009707)
    '''

    surf_roughB: RefinableFloat = Field(
        # serialization_alias='SurfRoughB',
        alias='SurfRoughB',
    )
    r'''
    Surface roughness correction for the intensity.  
    The factor is given by  
    $[\mathrm{A} + (1-\mathrm{A})\exp(-\mathrm{B}/\sin\theta)] / \mathrm{C}$,  
    where $\mathrm{C} = \mathrm{A} + (1-\mathrm{A})\exp(-\mathrm{B})$ is the normalization factor.  
    [P. Suortti, *J. Appl. Cryst.* **5**, 325 (1972)](https://doi.org/10.1107/S0021889872009707)
    '''
    
SampleParameters = Annotated[
    Union[
        SampleParametersDebyeScherrerCW,
        SampleParametersDebyeScherrerTOF,
        SampleParametersBraggBrentano
    ],
    Field(discriminator = 'type')
]

class InstrumentParametersBase(ClientModel):

    X: RefinableFloat
    r'''
    Lorentzian instrumental broadening parameter.  
    FWHM is given by  
    $\mathrm{X}/\cos\theta + \mathrm{Y}\tan\theta + \mathrm{Z}$ for CW measurements  
    and $\mathrm{X}d + \mathrm{Y}d^2 + Z$ for TOF measurements.
    '''

    Y: RefinableFloat
    r'''
    Lorentzian instrumental broadening parameter.  
    FWHM is given by  
    $\mathrm{X}/\cos\theta + \mathrm{Y}\tan\theta + \mathrm{Z}$ for CW measurements  
    and $\mathrm{X}d + \mathrm{Y}d^2 + Z$ for TOF measurements.
    '''

    Z: RefinableFloat
    r'''
    Lorentzian instrumental broadening parameter.  
    FWHM is given by  
    $\mathrm{X}/\cos\theta + \mathrm{Y}\tan\theta + \mathrm{Z}$ for CW measurements  
    and $\mathrm{X}d + \mathrm{Y}d^2 + Z$ for TOF measurements.
    '''

    zero: RefinableFloat = Field(
        # serialization_alias='Zero',
        alias='Zero',
    )
    r'''
    Zero point correction for
    - 2$\theta$ in CW measurements in degrees
    - flight time in TOF measurements in microseconds
    '''

class InstrumentParametersPowderCW(InstrumentParametersBase):

    U: RefinableFloat
    r'''
    The Gaussian instrumental broadening parameter.  
    FWHM is given by
    $\sqrt{\mathrm{U}{\tan}^2\theta + \mathrm{V}\tan\theta + \mathrm{W}}$
    '''

    V: RefinableFloat
    r'''
    The Gaussian instrumental broadening parameter.  
    FWHM is given by
    $\sqrt{\mathrm{U}{\tan}^2\theta + \mathrm{V}\tan\theta + \mathrm{W}}$
    '''

    W: RefinableFloat
    r'''
    The Gaussian instrumental broadening parameter.  
    FWHM is given by
    $\sqrt{\mathrm{U}{\tan}^2\theta + \mathrm{V}\tan\theta + \mathrm{W}}$
    '''

    polariz: RefinableFloat = Field(
        # serialization_alias='Polariz.',
        alias='Polariz.',
    )
    r'''
    Polarization correction for the intensity.  
    The factor is given by  
    $\{(1-P)\cos^2\phi_\mathrm{az} + P\sin^2\phi_\mathrm{az}\}\cos^22\theta + (1-P)\sin^2\phi_\mathrm{az} + P\cos^2\phi_\mathrm{az}$,  
    where $P$ is the fraction of the electric field porlarization of an incident X-ray  
    and $\phi_\mathrm{az}$ is the azimuthal angle in the Debye-Scherrer ring  
    ($\phi_\mathrm{az}=0$ at the direction normal to the polarization plane).  
    For an unpolarized beam, $P=0.5$.  
    For a sychrotron X-ray, $P$ generally ranges from $0.8$ to $1$  
    when considering the polarization direction in the orbital plane of the sychrotron.  
    [L.V. Azaroff, Acta Cryst. **8**, 701 (1955)](https://doi.org/10.1107/S0365110X55002156)  
    [R.B. Von Dreele and W. Xu, J. Appl. Cryst. **53**, 1559 (2020)](https://doi.org/10.1107/S1600576720014132)
    '''

    SH_L: RefinableFloat = Field(
        # serialization_alias='SH/L',
        alias='SH/L',
    )
    r'''
    Asymmetric peak broadening ratio, $(S+H)/L$,  
    of [the Finger-Cox-Jephcoat modified Pseudo-Voigt function](https://doi.org/10.1107/S0021889894004218),  
    where $S$ and $H$ are sample and slit heights and $L$ is the goniometer diameter.  
    '''

class InstrumentParametersPXC(InstrumentParametersPowderCW):
    type: Literal['PXC'] = 'PXC'
    I2_I1: RefinableFloat = Field(
        # serialization_alias='I(L2)/I(L1)',
        alias='I(L2)/I(L1)',
    )
    r'''
    The intensity ratio of $\alpha_2$ to $\alpha_1$ of a characteristic x-ray beam.
    '''

class InstrumentParametersPNC(InstrumentParametersPowderCW):
    type: Literal['PNC'] = 'PNC'

class InstrumentParametersTOF(InstrumentParametersBase):
    type: Literal['PNT'] = 'PNT'
    r'''
    It is apparently unused in calculations of GSAS-II.  
    The difC is used for the conversion from TOF to d-space instead.
    '''

    sig0: RefinableFloat = Field(
        # serialization_alias='sig-0',
        alias='sig-0',
    )
    r'''
    $\sigma = \sigma_0 + \sigma_1d^2 + \sigma_2d^4 + \sigma_\mathrm{q}d$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

    sig1: RefinableFloat = Field(
        # serialization_alias='sig-1',
        alias='sig-1',
    )
    r'''
    $\sigma = \sigma_0 + \sigma_1d^2 + \sigma_2d^4 + \sigma_\mathrm{q}d$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

    sig2: RefinableFloat = Field(
        # serialization_alias='sig-2',
        alias='sig-2',
    )
    r'''
    $\sigma = \sigma_0 + \sigma_1d^2 + \sigma_2d^4 + \sigma_\mathrm{q}d$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

    sigq: RefinableFloat = Field(
        # serialization_alias='sig-q',
        alias='sig-q',
    )
    r'''
    $\sigma = \sigma_0 + \sigma_1d^2 + \sigma_2d^4 + \sigma_\mathrm{q}d$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

    alpha: RefinableFloat
    r'''
    $\alpha_1$ of $\alpha = \alpha_1/d$,  
    where $\alpha$ represents the exponetial rise of an asymmetric peak in the *double exponetial pseudo-Voigt convolution function*.  
    It appears to be a convolution between the pseudo-Voigt  
    and a pair of $\exp(\alpha\tau)$ for the shorter side and $\exp(-\beta\tau)$ for the longer side of a peak profile, where $\tau$ is the flight time.  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)  
    [R.B. Von Dreele *et al.*, J. Appl. Cryst. **15**, 581 (1982)](https://doi.org/10.1107/S0021889882012722)  
    [R.B. Von Dreele *et al.*, J. Appl. Cryst. **54**, 3 (2021)](https://doi.org/10.1107/S1600576720014624)
    '''

    beta0: RefinableFloat = Field(
        # serialization_alias='beta-0',
        alias='beta-0',
    )
    r'''
    $\beta = \beta_0 + \beta_1/d^4 + \beta_\mathrm{q}/d^2$,  
    where $\beta$ is the slow exponential decay of an asymmetric peak in the *double exponential pseudo-Voigt convolution function*.  
    See the description of $\alpha$ for more details.
    '''

    beta1: RefinableFloat = Field(
        # serialization_alias='beta-1',
        alias='beta-1',
    )
    r'''
    $\beta = \beta_0 + \beta_1/d^4 + \beta_\mathrm{q}/d^2$,  
    where $\beta$ is the slow exponential decay of an asymmetric peak in the *double exponential pseudo-Voigt convolution function*.  
    See the description of $\alpha$ for more details.
    '''

    betaq: RefinableFloat = Field(
        serialization_alias='beta-q',
        alias='beta-q',
    )
    r'''
    $\beta = \beta_0 + \beta_1/d^4 + \beta_\mathrm{q}/d^2$,  
    where $\beta$ is the slow exponential decay of an asymmetric peak in the *double exponential pseudo-Voigt convolution function*.  
    See the description of $\alpha$ for more details.
    '''

    difA: RefinableFloat
    r'''
    $\mathrm{TOF} = \mathrm{difC}\cdot d + \mathrm{difA}\cdot d^2 + \mathrm{difB}/d + zero$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

    difB: RefinableFloat
    r'''
    $\mathrm{TOF} = \mathrm{difC}\cdot d + \mathrm{difA}\cdot d^2 + \mathrm{difB}/d + zero$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

    difC: RefinableFloat
    r'''
    $\mathrm{TOF} = \mathrm{difC}\cdot d + \mathrm{difA}\cdot d^2 + \mathrm{difB}/d + zero$  
    [A. Huq *et al.*, J. Appl. Cryst. **52**, 1189 (2019)](https://doi.org/10.1107/S160057671901121X)
    '''

InstrumentParameters = Annotated[
    Union[
        InstrumentParametersPXC,
        InstrumentParametersPNC,
        InstrumentParametersTOF,
    ],
    Field(discriminator = 'type')
]

class LatticeParameters(ClientModel):
    a: ConstrainableFloat
    b: ConstrainableFloat
    c: ConstrainableFloat
    alpha: ConstrainableFloat
    beta: ConstrainableFloat
    gamma: ConstrainableFloat
    volume: Optional[ErrorPropergatedFloat] = None


class AtomParametersBase(ClientModel):
    x: ConstrainableFloat
    y: ConstrainableFloat
    z: ConstrainableFloat
    frac: RefinableFloat

class AtomParametersIsotropic(AtomParametersBase):
    adp_model: Literal['isotropic'] = 'isotropic'
    Uiso: RefinableFloat

class AtomParametersAnisotropic(AtomParametersBase):
    adp_model: Literal['anisotropic'] = 'anisotropic'
    U11: ConstrainableFloat
    U22: ConstrainableFloat
    U33: ConstrainableFloat
    U12: Optional[ConstrainableFloat] = None
    U13: Optional[ConstrainableFloat] = None
    U23: Optional[ConstrainableFloat] = None

AtomParameters = Annotated[
    Union[
        AtomParametersIsotropic,
        AtomParametersAnisotropic,
    ],
    Field(discriminator='adp_model')
]

class Fractions(ClientModel):
    phase_scale: RefinableFloat
    wgt_frac: Optional[ErrorPropergatedFloat] = None
    mol_frac: Optional[ErrorPropergatedFloat] = None


class IsotropicSizeModel(ClientModel):
    model:Literal['isotropic'] = 'isotropic'
    size: RefinableFloat # 0 <= size <= 10
    LGmix: RefinableFloat

class UniaxialSizeModel(ClientModel):
    model: Literal['uniaxial'] = 'uniaxial'
    unique_axis: MillerIndex
    equatorial: RefinableFloat
    axial: RefinableFloat
    LGmix: RefinableFloat

class EllipsoidalSizeModel(ClientModel):
    model: Literal['ellipsoidal'] = 'ellipsoidal'
    S11: RefinableFloat
    S22: RefinableFloat
    S33: RefinableFloat
    S12: RefinableFloat
    S13: RefinableFloat
    S23: RefinableFloat
    LGmix: RefinableFloat

SizeModel = Annotated[
    Union[
        IsotropicSizeModel,
        UniaxialSizeModel,
        EllipsoidalSizeModel,
    ],
    Field(discriminator='model')
]

class IsotropicMustrainModel(ClientModel):
    model: Literal['isotropic'] = 'isotropic'
    strain: RefinableFloat
    LGmix: RefinableFloat

class UniaxialMustrainModel(ClientModel):
    model: Literal['uniaxial'] = 'uniaxial'
    unique_axis: MillerIndex
    equatorial: RefinableFloat
    axial: RefinableFloat
    LGmix: RefinableFloat

class GeneralizedMustrainModel(ClientModel):
    model: Literal['generalized'] = 'generalized'
    S400: RefinableFloat
    S040: Optional[RefinableFloat] = None
    S004: Optional[RefinableFloat] = None
    S220: Optional[RefinableFloat] = None
    S202: Optional[RefinableFloat] = None
    S022: Optional[RefinableFloat] = None
    S310: Optional[RefinableFloat] = None
    S103: Optional[RefinableFloat] = None
    S031: Optional[RefinableFloat] = None
    S130: Optional[RefinableFloat] = None
    S301: Optional[RefinableFloat] = None
    S013: Optional[RefinableFloat] = None
    S211: Optional[RefinableFloat] = None
    S121: Optional[RefinableFloat] = None
    S112: Optional[RefinableFloat] = None
    LGmix: RefinableFloat

MustrainModel = Annotated[
    Union[
        IsotropicMustrainModel,
        UniaxialMustrainModel,
        GeneralizedMustrainModel,
    ],
    Field(discriminator='model')
]

class MarchDollaseModel(ClientModel):
    model: Literal['March-Dollase'] = 'March-Dollase'
    ratio: RefinableFloat
    unique_axis: MillerIndex

class SphericalHarmonicsModel(ClientModel):
    model: Literal['Spherical-Harmonics'] = 'Spherical-Harmonics'
    order: int = Field(multiple_of=2, ge=0, le=32)
    coeffs: RefinableFloatList
    names: Optional[list[str]] = None # GSASIIlattice.GenSHCoeff
    penaltyHKL: Optional[list[str]] = None # c.f. maybe ['h0 k0 l0', 'h1 k1 l1']
    zeroMRDtoler: Optional[float] = None

    @model_validator(mode='after')
    def validate_length(self):
        if self.names is None:
            return self
        if len(self.coeffs.values) != len(self.names):
            raise ValueError(f'The coeffs and names should be equal in length.')
        return self

PreferredOrientationModel = Annotated[
    Union[
        MarchDollaseModel,
        SphericalHarmonicsModel,
    ],
    Field(discriminator='model')
]

class HydrostaticStrainModel(ClientModel):
    D11: Optional[RefinableFloat] = None
    eA: Optional[RefinableFloat] = None
    D22: Optional[RefinableFloat] = None
    D33: Optional[RefinableFloat] = None
    D12: Optional[RefinableFloat] = None
    D13: Optional[RefinableFloat] = None
    D23: Optional[RefinableFloat] = None

# class LayerDisplacementModel(BaseModel):
#     layer_disp: RefinableFloat

# class ExtinctionModel(BaseModel):
#     extinction: RefinableFloat

class BabinetModel(ClientModel):
    A: RefinableFloat
    U: RefinableFloat

class HistogramPhaseParameters(ClientModel):
    frac: Fractions
    size: Optional[SizeModel] = None
    mustrain: Optional[MustrainModel] = None
    hstrain: Optional[HydrostaticStrainModel] = None
    # layer_disp: LayerDisplacementModel|None = None
    layer_disp: Optional[RefinableFloat] = None
    pref_ori: Optional[PreferredOrientationModel] = None
    # extinction: ExtinctionModel|None = None
    extinction: Optional[RefinableFloat] = None
    babinet: Optional[BabinetModel] = None

class PhaseParameters(ClientModel):
    LP: LatticeParameters
    atoms: dict[str, AtomParameters]
    HAP: HistogramPhaseParameters

class PolynomialBackground(ClientModel):
    func: Literal[
        'chebyschev',
        'cosine',
        'chebyschev-1',
        'Q^2 power series',
        'Q^-2 power series',
        'lin interpolate',
        'inv interpolate',
        'log interpolate',
    ]
    r'''
    **Chebyschev** : $\displaystyle \sum_{i=0}^{n-1} \mathrm{c}_i \left(-1+2\frac{x-x_0}{x_\mathrm{N}-2x_0}\right)^i$

    **Chebyschev-1** : $\displaystyle \sum_{i=0}^{n-1} \mathrm{c}_i \cos\left[i\cos^{-1}\left(-1+2\frac{x-x_0}{x_\mathrm{N}-x_0}\right)\right]$

    **Cosine** : $\displaystyle \sum_{i=0}^{n-1} \mathrm{c}_i \cos\left(\frac{i\pi x}{x_\mathrm{N}}\right)$

    **$\mathbf{Q^2}$ power series** : $\displaystyle \sum_{i=0}^{n-1} \mathrm{c}_i \frac{q^{2i}}{i!}$

    **$\mathbf{Q^{-2}}$ power series** : $\displaystyle \sum_{i=0}^{n-1} \mathrm{c}_i \frac{i!}{q^{2i}}$

    **Lin-interpolate** : Linear interpolation of coordinates $\{(x_i^\mathrm{lin}, c_i)\}$,  
    where $x_i^\mathrm{lin}$ denotes the $i$ th equidistant point obtained by dividing the $x$ range into $n-1$ equal intervals.  
    It is constant and equal to $c_0$ when $n=1$.

    **Inv-interpolate** : Linear interpolation of coordinates $\{(x_i^\mathrm{inv}, c_i)\}$,  
    where $x_i^\mathrm{inv}$ denotes the $i$ th point obtained by first dividing the range $[1/x_\mathrm{N}, 1/x_0]$ into $n-1$ equal intervals,  
    and then taking the reciprocal of each division point to map them back to the original scale.  
    It is constant and equal to $c_0$ when $n=1$.

    **Log-interpolate** : Linear interpolation of coordinates $\{(x_i^\mathrm{log}, c_i)\}$,  
    where $x_i^\mathrm{log}$ denotes the $i$ th point obtained by first dividing the range $[\log x_0, \log x_\mathrm{N}]$ into $n-1$ equal intervals,  
    and then applying the exponential function to each division point to map them back to the original scale.  
    It is constant and equal to $c_0$ when $n=1$.

    - $c_i$ is the coefficient of the $i$ th component. The total number of components is $n$.
    - $x$ represents either $2\theta$ or time-of-flight.
    - $x_0$ and $x_\mathrm{N}$ are the lower and upper bounds of the $x$ range considered.
    - $q = 4\pi\sin\theta/\lambda$ or $2\pi t/\mathrm{difC}$
    '''
    
    coeffs: RefinableFloatList

class DebyeDiffuseBackground(ClientModel):
    '''A * sin(qR) * exp(-Uq^2) / qR'''
    A: RefinableFloat
    R: RefinableFloat
    U: RefinableFloat

class PeakBackground(ClientModel):
    '''FCJ-pseudo-voigt.
    The asymmetry parameter SH/L is also concerned'''
    position: RefinableFloat
    intensity: RefinableFloat
    sigma: RefinableFloat
    gamma: RefinableFloat

class BackgroundParameters(ClientModel):
    polynomial: PolynomialBackground
    debyes: list[DebyeDiffuseBackground] = []
    peaks: list[PeakBackground] = []

class RefinementParameters(ClientModel):
    algorithm: str
    converged_ifdMM_lt: float
    max_cycles: int
    SVD_zero_tolerance: float
    upper_limit: float
    lower_limit: float
    constraints: dict
    restraints: dict
    rigid_bodies: dict

class Rvalues(ClientModel):
    aborted: bool
    converged: bool
    Rwp: Optional[float]
    GOF: Optional[float]
    chi2: Optional[float]
    message: Optional[str]
    SVD0: int
    SVDvars: list[str]
    maxlam: Optional[float]
    strongly_correlated_pairs: list[list]
    Nvar: Optional[int]
    Nobs: Optional[int]
    Nvarholded: list[str]
    cycles: Optional[int]


class RefineBasemodel(ClientModel):
    sequence_index: int  # one or larger
    SP: SampleParameters
    IP: InstrumentParameters
    phases : dict[str, PhaseParameters]
    BP: BackgroundParameters
    RP: RefinementParameters
    Rval: Rvalues


class Refine(RefineBasemodel):
    id: str = Field(validation_alias='_id')
    # parent_trial: Link['Trial']
    parent_trial: Link
    group: Link
    start_at: datetime
    time_to_complete: timedelta


class Trial(ClientModel):
    id: str = Field(validation_alias='_id')
    parent_study: Link
    group: Link
    refines: list[Link]
    result_refine: Optional[RefineBasemodel]
    num: int = Field(validation_alias='trial_num')
    is_randomly_sampled: bool
    seed: int
    start_at: datetime
    time_to_complete: timedelta
    processed_by: str
