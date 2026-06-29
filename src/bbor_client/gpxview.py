import re
from typing import Literal
import pandas as pd
from pathlib import Path

import plotly.graph_objects as go
import plotly.colors as pcolors
import myPlotlyStyle

from GSASII.GSASIIscriptable import G2Project, G2PwdrData, G2Phase, G2AtomRecord, SetPrintLevel
from GSASII.GSASIIElem import GetElInfo
from GSASII.GSASIIlattice import CellAbsorption
from GSASII.GSASIIspc import MustrainNames

from .conf import MFILE_SUFFIXES, CIF_SUFFIXES, PRM_SUFFIXES

def load_gpx(
    inputdir: Path|str|None = None,
    gpxfile: Path|str|None = None,
    mfile: Path|str|None = None,
    prmfile: Path|str|None = None,
    ciffiles: list[Path|str]|None = None,
    newgpx: Path|str = './temp.gpx',
    Uiso: bool = True,
    verbose: Literal['all', 'warn', 'error', 'none'] = 'warn',
):
    SetPrintLevel(verbose)
    if inputdir is not None:
        inputdir = Path(inputdir)
        ciffiles = []
        for file in inputdir.iterdir():
            if file.suffix.lower().endswith('.gpx'):
                gpxfile = file
                break
            elif file.suffix.lower().endswith(MFILE_SUFFIXES):
                mfile = file
                continue
            elif file.suffix.lower().endswith(PRM_SUFFIXES):
                prmfile = file
                continue
            elif file.suffix.lower().endswith(CIF_SUFFIXES):
                ciffiles.append(file)
                continue
    if gpxfile is not None:
        gpx = G2Project(
            gpxfile = gpxfile,
            newgpx = newgpx,
        )
    else:
        assert isinstance(ciffiles, list)
        gpx = G2Project(newgpx=newgpx)
        hist = gpx.add_powder_histogram(mfile, prmfile)
        for cif in ciffiles:
            cif = Path(cif)
            _ = gpx.add_phase(
                phasefile = cif,
                phasename = cif.stem,
                histograms = [hist],
            )
        if Uiso:
            for phase in gpx.phases():
                assert isinstance(phase, G2Phase)
                for atom in phase.atoms():
                    assert isinstance(atom, G2AtomRecord)
                    atom.data[atom.cia] == 'I' # type: ignore
    return gpx


def reflection_df(
        phase: G2Phase,
        gpx: G2Project,
) -> pd.DataFrame:
    '''
    Returns a dataframe of reflecting planes of a phase.
    '''
    hist = gpx.histogram(0)
    assert isinstance(hist, G2PwdrData)
    reflist = hist.reflections()[phase.name]['RefList']
    if len(reflist[0])==15: # CW
        columns = ('H','K','L','mul','d','2th','sigma','gamma','Fosq','Fcsq','phase','Icorr','Prfo','Trans','ExtP')
    elif len(reflist[0])==18: # TOF
        columns = (
            'H', 'K', 'L', 'mul', 'd', 'TOF', 'sig', 'gam', 'Fosq', 'Fcsq', 'phase', 'Icorr',
            'alpha', 'beta', 'wavelength', 'Prfo', 'Trans', 'ExtP',
        )
    else:
        raise ValueError(f'len({reflist[0]})=')
    df = pd.DataFrame(
        data = reflist,
        columns = columns,
        dtype = float,
    ).astype({'H':int, 'K':int, 'L':int,'mul':int})
    df['HKL'] = df['H'].astype(str) + df['K'].astype(str) + df['L'].astype(str)
    return df


def plot_fitline(
        gpx: G2Project,
        title: str|None = None,
        showDiff: bool = True,
        showIndex: bool = True,
):
    '''
    Show a line chart of a measured histogram, a fitline, a background component, and the difference of the histogram and fitline.
    '''
    colors = pcolors.qualitative.G10
    hist = gpx.histogram(0)
    assert isinstance(hist, G2PwdrData)
    isCW = 'C' in hist.InstrumentParameters['Type'][0]
    fig = go.Figure()
    fig.update_layout(
        template = 'mystyle',
        title_text = title,
        xaxis_title_text = 'Two theta' if isCW else 'TOF',
        yaxis_title_text = 'Counts or Intensity',
        yaxis2 = dict(
            side='right',
            showgrid=False,
            overlaying='y',
            range=[0,100],
            ticks='',
            minor_ticks='',
            showticklabels=False,
            fixedrange=True
        ),
    )
    fig.add_scatter(
        x = hist.getdata('X'),
        y = hist.getdata('Yobs'),
        name = 'obs',
    )
    fig.add_scatter(
        x = hist.getdata('X'),
        y = hist.getdata('Ycalc'),
        name = 'fit',
    )
    fig.add_scatter(
        x = hist.getdata('X'),
        y = hist.getdata('background'),
        name = 'bkg',
        line = dict(
            width = 0.5,
            color = 'grey',
        )
    )
    if showDiff:
        fig.add_scatter(
            x = hist.getdata('X'),
            y = hist.getdata('residual'),
            name = 'diff',
            line = dict(
                width = 0.5,
            ),
        )
    if showIndex:
        for i,phase in enumerate(gpx.phases()):
            assert isinstance(phase, G2Phase)
            df = reflection_df(phase, gpx)
            fig.add_scatter(
                x = df['2th'] if isCW else df['TOF'],
                y = [4+2*i] * len(df),
                yaxis = 'y2',
                mode='markers',
                marker=dict(
                    symbol='line-ns',
                    size=3,
                    line_width=1,
                    color=colors[i+5],
                    line_color=colors[i+5]
                ),
                hovertext=df['HKL'],
                name = phase.name,
                hoverinfo='name+text',
                showlegend = False,
            )
    fig.show()



def print_parameters(
        gpx: G2Project,
        showIP: bool = True,
        showSP: bool = True,
        showLP: bool = False,
        showHAP: bool = True,
        showAP: bool = True,
        showBP: bool = False,
):
    '''
    Print most parameters to check.
    Note that not all are printed.
    '''
    hist = gpx.histogram(0)
    assert isinstance(hist, G2PwdrData)
    if showIP:
        for ip in ('U','V','W','X','Y','Z','SH/L','Zero'):
            print(f'{ip:>4} = {hist.InstrumentParameters[ip][1]}')
    if showSP:
        for sp in ('Scale', 'Shift', 'SurfRoughB'):
            print(f'{sp:>4} = {hist.SampleParameters[sp][0]}')
    for phase in gpx.phases():
        assert isinstance(phase, G2Phase)
        SGData = phase['General']['SGData']
        print(f'{phase.name}')
        if showLP:
            a = phase.get_cell()['length_a']
            b = phase.get_cell()['length_b']
            c = phase.get_cell()['length_c']
            alpha = phase.get_cell()['angle_alpha']
            beta = phase.get_cell()['angle_beta']
            gamma = phase.get_cell()['angle_gamma']
            print(f'    a,b,c,\u03B1,\u03B2,\u03B3={(a,b,c,alpha,beta,gamma)}')
        if showHAP:
            print(f'    scale = {phase.getHAPvalues(hist)["Scale"][0]}')

            type=phase.getHAPvalues(hist)['Size'][0]
            value = phase.getHAPvalues(hist)['Size'][1][0]
            refines = phase.getHAPvalues(hist)['Size']
            if not (type=='isotropic' and value==1.0 and all(refines)):
                print(f'    size : {type}')
                if type == 'isotropic':
                    print(f'        value = {phase.getHAPvalues(hist)["Size"][1][0]}')
                elif type == 'uniaxial':
                    print(f'        equatorial = {phase.getHAPvalues(hist)["Size"][1][0]}')
                    print(f'        axial = {phase.getHAPvalues(hist)["Size"][1][1]}')
                    print(f'        axis = {phase.getHAPvalues(hist)["Size"][3]}')
                elif type == 'ellipsoidal':
                    print(f'        S11 = {phase.getHAPvalues(hist)["Size"][4][0]}')
                    print(f'        S22 = {phase.getHAPvalues(hist)["Size"][4][1]}')
                    print(f'        S33 = {phase.getHAPvalues(hist)["Size"][4][2]}')
                    print(f'        S12 = {phase.getHAPvalues(hist)["Size"][4][3]}')
                    print(f'        S13 = {phase.getHAPvalues(hist)["Size"][4][4]}')
                    print(f'        S23 = {phase.getHAPvalues(hist)["Size"][4][5]}')
                print(f'        LGmix = {phase.getHAPvalues(hist)["Size"][1][2]}')

            type=phase.getHAPvalues(hist)['Mustrain'][0]
            value = phase.getHAPvalues(hist)['Mustrain'][1][0]
            refines = phase.getHAPvalues(hist)['Mustrain']
            if not (type=='isotropic' and value==1000.0 and all(refines)):
                print(f'    microstrain : {type}')
                if type == 'isotropic':
                    print(f'        value = {phase.getHAPvalues(hist)["Mustrain"][1][0]}')
                elif type == 'uniaxial':
                    print(f'        equatorial = {phase.getHAPvalues(hist)["Mustrain"][1][0]}')
                    print(f'        axial = {phase.getHAPvalues(hist)["Mustrain"][1][1]}')
                    print(f'        axis = {phase.getHAPvalues(hist)["Mustrain"][3]}')
                elif type == 'generalized':
                    msnames = MustrainNames(SGData)
                    values = phase.getHAPvalues(hist)['Mustrain'][4]
                    if len(values)==len(msnames):
                        for v,name in zip(values, msnames):
                            print(f'        {name} = {v}')
                print(f'        LGmix = {phase.getHAPvalues(hist)["Mustrain"][1][2]}')

            type = phase.getHAPvalues(hist)['Pref.Ori.'][0]
            value = phase.getHAPvalues(hist)['Pref.Ori.'][1]
            refine = phase.getHAPvalues(hist)['Pref.Ori.'][2]
            if not (type=='MD' and value==1.0 and refine==False):
                print(f'    preferred orientation : {type}')
                if type == 'MD':
                    print(f'        value = {phase.getHAPvalues(hist)["Pref.Ori."][1]}')
                    print(f'        axis = {phase.getHAPvalues(hist)["Pref.Ori."][3]}')

        if showAP:
            for atom in phase.atoms():
                print(f'    {atom.label}')
                print(f'        x,y,z = {atom.coordinates}')
                print(f'        occupancy = {atom[atom.cx+3]}')
                if atom.adp_flag=='I':
                    print(f'        Uiso = {atom.uiso}')
                if atom.adp_flag=='A':
                    print(f'        U11 = {atom[atom.cia+2]}')
                    print(f'        U22 = {atom[atom.cia+3]}')
                    print(f'        U33 = {atom[atom.cia+4]}')
                    print(f'        U12 = {atom[atom.cia+5]}')
                    print(f'        U13 = {atom[atom.cia+6]}')
                    print(f'        U23 = {atom[atom.cia+7]}')

    if showBP:
        print(f'Background: {hist.Background[0][0]}')
        print(f'    values = {hist.Background[0][3:]}')





def linear_absorption_coefficients(gpx: G2Project) -> dict[str, float]:
    hist = gpx.histogram(0)
    if not isinstance(hist, G2PwdrData):
        raise ValueError('Gpx histogram is not powder data')
    atom_label_pattern = r'([A-Z][a-z]?)(?:[+-]\d+)?'
    mus = {}
    for phase in gpx.phases():
        if phase is None: continue
        ElList = {}
        for ionlabel,num in phase['General']['NoAtoms'].items():
            match_ = re.match(atom_label_pattern, ionlabel)
            if match_:
                elem = match_.group(1)
            else:
                print(f'Failed to match {ionlabel=}')
                continue
            ElData = GetElInfo(elem, hist.InstrumentParameters)
            ElData['FormulaNo'] = float(num)
            ElList[elem] = ElData
        volume = phase['General']['Cell'][7]
        mu = CellAbsorption(ElList, volume)
        mus[phase.name] = mu
    return mus






