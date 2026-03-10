"""
e3sm_util.py

Utility functions to aid with plotting & analysis of E3SM output.
Last updated: February 5, 2025

Functions:
    * mask_land: mask a DataArray or Dataset by the land fraction (i.e., get ocean- or land-only)
    * weighted_mean: compute a weighted average of a Dataset or DataArray
"""
import glob
import multiprocessing as mp
import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt

from scipy.interpolate import griddata
from matplotlib import cm, colors


# path to grid file (ne30pg2) on Derecho
GRID = "/glade/campaign/work/zender/grids/ne30pg2.nc"


def mask_land(ds, value, regridded=False,
              land_mask_file="/glade/campaign/uwyo/wyom0191/ppev0/processed/E3SMv3_land_mask.nc"):
    """ 
    Mask DataArray/Dataset by where the land fraction exceeds `value` (=0, >0.5, >0.9, or =1).
    Use value=0 to get ocean only, use value=1 to get land only, and use value = 0.5 or 0.9 to allow
    some coastlines, etc. 

    The masks are boolean DataArrays where True means keep the data and False means exclude the data.
    """
    if value == 0:
        if regridded:
            var_lm = "land_mask_regrid_0"
        else:
            var_lm = "land_mask_0"
    elif value == 0.5:
        if regridded:
            var_lm = "land_mask_regrid_05"
        else:
            var_lm = "land_mask_05"
    elif value == 0.9:
        if regridded:
            var_lm = "land_mask_regrid_09"
        else:
            var_lm = "land_mask_09"
    elif value == 1:
        if regridded:
            var_lm = "land_mask_regrid_1"
        else:
            var_lm = "land_mask_1"
    else:
        raise Exception("Currently only land masks of 0, 0.5, 0.9, or 1 are supported; {v} was passed in".format(v=value))
        
    land_mask = xr.open_dataset(land_mask_file)[var_lm]

    return ds.where(land_mask)


def weighted_mean(ds, dims=None, grid=GRID):
    """
    Compute weighted mean over `dims` in the dataset or data array using grid cell areas as
    the weights. If dims=None, computes the mean over all dimensions.
    """
    grid_area = xr.open_dataset(grid)["grid_area"].rename({"grid_size": "ncol"})
    
    if dims is not None:
        ds_wavg = ds.weighted(grid_area).mean(dim=dims)
    else:
        ds_wavg = ds.weighted(grid_area).mean()

    return ds_wavg

