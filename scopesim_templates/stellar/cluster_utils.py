from pathlib import Path

import numpy as np
from astropy.io.ascii import read as read_ascii
from scipy.interpolate import interp1d

import pyckles


DIRNAME = Path(__file__).parent
MAMAJEK = read_ascii(DIRNAME / "mamajek_alt.dat", delimiter="|")
F_MASS2MV = interp1d(MAMAJEK["Msun"], MAMAJEK["Mv"], 1)
F_MASS2IDX = interp1d(MAMAJEK["Msun"], range(len(MAMAJEK["Msun"])), 0)
PICKLES = pyckles.SpectralLibrary("pickles")

tbl = PICKLES.catalog[1].data
mask_evol = tbl["evolution"] == 5
mask_metal = tbl["metalicity"] == "normal"
PICKLES_MS_V = tbl["name"][mask_evol * mask_metal]


def mass2spt(mass):
    if isinstance(mass, (list, np.ndarray)):
        return [mass2spt(m) for m in mass]
    ii = int(F_MASS2IDX(mass))
    return MAMAJEK["SpT"][ii]


def mass2Mv(mass):
    if isinstance(mass, (list, np.ndarray)):
        return [mass2Mv(m) for m in mass]
    return F_MASS2MV(mass)


def closest_pickles(spt):
    if isinstance(spt, (list, np.ndarray)):
        return [closest_pickles(s) for s in spt]

    mask_lum = np.array([spt[0] in pic_spt for pic_spt in PICKLES_MS_V])
    lum_types = PICKLES_MS_V[mask_lum]
    classes = np.array([float(lt[1:-1]) for lt in lum_types])
    ii = np.argmin(np.abs(classes - float(spt[1:-1])))
    closest_pickle = lum_types[ii]

    return closest_pickle


def king_distribution(n, r_core, r_tidal):
    from astropy.modeling.functional_models import KingProjectedAnalytic1D
    king = KingProjectedAnalytic1D(r_core=r_core, r_tidal=r_tidal)
    y = king(np.linspace(0, r_tidal, 100))

    return None


def gaussian_distribution(n, fwhm, seed=None):
    if isinstance(seed, int):
        np.random.seed(seed)
    x, y = np.random.normal(loc=0, scale=fwhm/2.35, size=(2, n))
    return x, y
