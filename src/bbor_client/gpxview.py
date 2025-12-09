import re
from typing import Literal
from pathlib import Path
from GSASII.GSASIIscriptable import G2Project, G2PwdrData, G2Phase, G2AtomRecord, SetPrintLevel
from GSASII.GSASIIElem import GetElInfo
from GSASII.GSASIIlattice import CellAbsorption
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






