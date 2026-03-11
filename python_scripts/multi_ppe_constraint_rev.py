"""
multi_ppe_constraint_rev.py

Functions to cosntrain PPEs by PD LWP, da/dlwp, and/or delta Nd;
option to save all calculated values/dicts as pickle files.
Also helper functions to find fit lines. 

**NOTE (as of March 2026)**: PD hemispheric Nd contrast stuff is left in here, but it was 
ultimately scrapped from this study since the PPE output Nd is not really
directly comparable to the MODIS Nd data, so that comparison doesn't actually
make sense... so those constraints in the dictionaries should be ignored!

Helper functions:
* linear
* quadratic
* pi_95 / pi_90
* get_dadlwp

Constraint functions:
* get_obs_constraints (obsolete function)
* get_obs_constraints_tol (use this on with err_tol=0 for no tolerance)
* read_obs_constraints

Stats functions:
* get_fit_line / read_fit_line
"""
import pickle
import numpy as np

from scipy import stats
from sklearn.metrics import r2_score


OUT_PATH = "/glade/u/home/jnug/work/multi_PPE_data/"

# Obs ranges
DELTA_ND = [8, 24] # PI-PD, derived from NH-SH contrast, from McCoy et al. (2020), PNAS
DELTA_ND_HEM = [32, 37] # NH-SH contrast, from McCoy et al. (2020), PNAS
PD_LWP = [65, 80] # MAC-LWP, from Song et al. (2024), GRL
DADLWP = [1.7, 2.1] # CERES, from Song et al. (2024), GRL


def linear(x, coeffs):
    """ Return y = m*x + b, where coeffs is [m, b]
    """
    return coeffs[0]*x + coeffs[1]


def quadratic(x, coeffs):
    """ Return y = a*x^2 + b*x + c, where coeffs is [a, b, c]
    """
    return coeffs[0]*(x**2) + coeffs[1]*x + coeffs[2]


def pi_95(arr, axis):
    """ Helper function to use in the bootstrap 95% prediction intervals
    """
    lower = np.percentile(arr, 2.5, axis=axis)
    upper = np.percentile(arr, 97.5, axis=axis)
    
    return np.stack([lower, upper], axis=0)


def pi_90(arr, axis):
    """ Helper function to use in the bootstrap 90% prediction intervals
    """
    lower = np.percentile(arr, 5, axis=axis)
    upper = np.percentile(arr, 95, axis=axis)
    
    return np.stack([lower, upper], axis=0)


def get_dadlwp(lwp, fit_file="/glade/u/home/jnug/work/multi_PPE_data/pickle_jar/lwp_inv__da_dlwp__fit.pickle"):
    """ 
    Get the albedo susceptibility (da/dlwp) from the fit function from
    Fig 2a, Song et al. (2024), GRL - given PD LWP.
    """
    with open(fit_file, "rb") as handle:
        fit_dict = pickle.load(handle)
    m = fit_dict["m"]
    b = fit_dict["b"]
    print(m, b)
    lwp_inv = 1/lwp
    dadlwp = m*lwp_inv + b

    return dadlwp


def get_obs_constraints_tol(ds, ppe, dnd_range_pipd=DELTA_ND, dnd_range_hem=DELTA_ND_HEM,
                            lwp_range=PD_LWP, dadlwp_range=DADLWP,
                            err_tol=0.05, save=False, out_path=OUT_PATH, constraints="all"):
    """ 
    Get a dictionary of lists of ensemble members that remain and/or are
    cut based on each individual constraint, and a total set of fully-constrained 
    ensemble members. (within the specified error tolerance; i.e., if err_tol=0.1, 
    obs +/- 10%).

    Input dataset ds must contain (at a minimum) data variables for delta_Nd (hem AND PD-PI),
    dadlwp, and LWP_pd_masked. 
    """
    dnd_min, dnd_max = dnd_range_pipd
    dnd_hem_min, dnd_hem_max = dnd_range_hem
    dadlwp_min, dadlwp_max = dadlwp_range
    lwp_min, lwp_max = lwp_range

    if err_tol > 0:
        dnd_min = dnd_min*(1 - err_tol)
        dnd_max = dnd_max*(1 + err_tol)
        dnd_hem_min = dnd_hem_min*(1 - err_tol)
        dnd_hem_max = dnd_hem_max*(1 + err_tol)
        dadlwp_min = dadlwp_min*(1 - err_tol)
        dadlwp_max = dadlwp_max*(1 + err_tol)
        lwp_min = lwp_min*(1 - err_tol)
        lwp_max = lwp_max*(1 + err_tol)

    extra = f"_error_tol_{err_tol}"
    all_members = ds.member.values

    # NH-SH AND PD-PI Nd
    dnd_hem_match = ds.where(((ds["delta_Nd_nhsh"] >= dnd_hem_min) & (ds["delta_Nd_nhsh"] <= dnd_hem_max)), drop=True).member.values
    dnd_pipd_match = ds.where(((ds["delta_Nd_ocn"] >= dnd_min) & (ds["delta_Nd_ocn"] <= dnd_max)), drop=True).member.values
        
    dadlwp_match = ds.where(((ds["dadlwp"] >= dadlwp_min) & (ds["dadlwp"] <= dadlwp_max)), drop=True).member.values
    lwp_match = ds.where(((ds["LWP_pd_masked"] >= lwp_min) & (ds["LWP_pd_masked"] <= lwp_max)), drop=True).member.values  

    # where all constraints match (using pipd)
    all_match = [x for x in dnd_pipd_match if (x in dadlwp_match and x in lwp_match)]

    # where all constraints match (using hem)
    all_match_hem = [x for x in dnd_hem_match if (x in dadlwp_match and x in lwp_match)]

    save_dict = {
        "delta_Nd_pipd": {"match": dnd_pipd_match, "cut": [x for x in all_members if x not in dnd_pipd_match]},
        "delta_Nd_hem": {"match": dnd_hem_match, "cut": [x for x in all_members if x not in dnd_hem_match]},
        "dadlwp": {"match": dadlwp_match, "cut": [x for x in all_members if x not in dadlwp_match]},
        "LWP_pd": {"match": lwp_match, "cut": [x for x in all_members if x not in lwp_match]},
        "all": {"match": all_match, "cut": [x for x in all_members if x not in all_match]},
        "all_ndhem": {"match": all_match_hem, "cut": [x for x in all_members if x not in all_match_hem]},
    }

    if save:
        with open(out_path + f"{ppe}_constrained_members_dict{extra}.pickle", "wb") as handle:
            pickle.dump(save_dict, handle)

    # to get a different combination of constraints - don't return the save_dict, only the new constraint dict
    if constraints != "all": 
        if isinstance(constraints, list):
            if len(constraints) == 1:
                constr_dict = save_dict[constraints[0]]
            elif len(constraints) == 2:
                match = [x for x in save_dict[constraints[0]]["match"] if x in save_dict[constraints[1]]["match"]]
                cut = [x for x in save_dict[constraints[0]]["cut"] if x in save_dict[constraints[1]]["cut"]]
                constr_dict = {"match": match, "cut": cut}
            else:
                # assume if there are three+ constraints that you want all (bc there's three total)
                constr_dict = save_dict["all"]
        else:
            constr_dict = save_dict[constraints]
        return constr_dict
        
    else:
        return save_dict


def read_obs_constraints(ppe, out_path=OUT_PATH, extra=""):
    """ Returns the saved pickle dictionary of ensemble member constraints for that PPE.
    """
    with open(out_path + f"{ppe}_constrained_members_dict{extra}.pickle", "rb") as handle:
        save_dict = pickle.load(handle)

    return save_dict


def get_fit_line(ppe, x, y, degree, save=False, varname=None, out_path=OUT_PATH+"pickle_jar/",
                print_r2=False):
    """ Get best fit line (some degree). Save a dictionary with the coefficients.
    """
    coeffs = np.polyfit(x, y, degree)
    if print_r2:
        pred = np.polyval(coeffs, x)
        print(f"{ppe}: r2 = {r2_score(y, pred):.3f}")
    
    if save:
        if varname is None:
            raise Exception("Must provide name of variable (\"varname\"=...) to save the fit coefficients")
        save_dict = {"fit": coeffs}
        name = f"{ppe}_{varname}_best_fit_degree={degree}.pickle"
        with open(out_path + name, "wb") as handle:
            pickle.dump(save_dict, handle)

    return coeffs


def read_fit_line(ppe, varname, degree, out_path=OUT_PATH):
    """ Read in the dictionary of coefficients for fit line
    """
    name = f"{ppe}_{varname}_best_fit_degree={degree}.pickle"
    with open(out_path + name, "rb") as handle:
        return pickle.load(handle)["fit"]
