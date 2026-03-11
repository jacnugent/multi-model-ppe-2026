import fair

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from fair import multi_ebm
from fair.energy_balance_model import EnergyBalanceModel


# to save proejctions
FAIR_OUT = "/glade/work/jnug/codes/e3sm-ppe-aci/analysis/notebooks/multi_PPE_adj/FAIR_projections/cmip6/"

# where files are stored
FILE_PATH = "/glade/work/jnug/multi_PPE_data/FaIR_data/"



def scale_aci_forcing(present_day_forcing, df_forcing, default=-0.84):
    """ 
    Scale present-day ERFaci in the perturbed values (present-day forcing) by a new value
    - to get a proportional increase/decrease over time
    """
    # scaled = ERFaci(E, theta) = ERFaci(theta) * ERFaci(E) / ERfaci(theta=theta_star)
    scaled = present_day_forcing.to_xarray() * df_forcing['aerosol-cloud_interactions'].to_xarray() / df_forcing['aerosol-cloud_interactions'].to_xarray().sel(year=slice(1850, 2010)).mean() 

    return scaled


def scale_ari_forcing(present_day_forcing, df_forcing, default=-0.84):
    """ 
    Scale present-day ERFari in the perturbed values (present-day forcing) by a new value
    - to get a proportional increase/decrease over time
    """
    # scaled = ERFaci(E, theta) = ERFaci(theta) * ERFaci(E) / ERfaci(theta=theta_star)
    scaled = present_day_forcing.to_xarray() * df_forcing['aerosol-radiation_interactions'].to_xarray() / df_forcing['aerosol-radiation_interactions'].to_xarray().sel(year=slice(1850, 2010)).mean() 

    return scaled


def get_pdf90(lower, upper, rng):
    """ Use bounds for 90% CI to get PDF
    """    
    # Estimated parameters from the 90% CI
    mu = (lower + upper) / 2 
    sigma = ( (upper - mu) / 1.645 )  # z=1.645 for 90% confidence.
    
    # Generate the PDF
    pdf90 = rng.normal(loc=mu, scale=sigma, size=5000)

    return pdf90


def calc_temperatures(climate_feedback, scaled_ERFaci, scaled_ERFari, historical_forcing_sans_aerosol,
                      df_forcing, model_params, seed=20250520, n_samples=1000):
    """ 
    Run FaIR to get projected temperature change from some ERFaci range.

    Returns all projected temperatures (as data array), first layer projected temperatures (as data frame),
    calculate ECS (as data array), calculate TOA energy imbalance (as data array).
    """
    _temperatures = []
    _ecs = []
    _toa_imb = []
    
    for i in range(len(climate_feedback)):
        ebm = EnergyBalanceModel(
            ocean_heat_capacity=[model_params.C1, model_params.C2, model_params.C3],
            ocean_heat_transfer=[climate_feedback.iloc[i].values[0], model_params.kappa2, model_params.kappa2],
            deep_ocean_efficacy=model_params.epsilon, 
            gamma_autocorrelation=model_params.gamma,  
            sigma_xi=model_params.sigma_xi,
            sigma_eta=model_params.sigma_eta,
            forcing_4co2=model_params.F_4xCO2,
            stochastic_run=False,
            seed=seed
        )

        forcing = historical_forcing_sans_aerosol.values + scaled_ERFaci[i].values + scaled_ERFari[i].values
        ebm.add_forcing(forcing=forcing, timestep=1)
        ebm.run()
        _temperatures.append(ebm.temperature[:,0])
        _toa_imb.append(ebm.toa_imbalance)

        # get ecs
        ebm.emergent_parameters()
        _ecs.append(ebm.ecs)

    ensemble_temperatures = xr.DataArray(np.array(_temperatures), dims=['ensemble', 'year'], coords={'ensemble':np.arange(n_samples), 'year':df_forcing.index})
    ensemble_ecs = xr.DataArray(np.array(_ecs), dims=['ensemble'], coords={'ensemble':np.arange(n_samples)})
    ensemble_toa_imb = xr.DataArray(np.array(_toa_imb), dims=['ensemble', 'year'], coords={'ensemble':np.arange(n_samples), 'year':df_forcing.index})


    ebm_tas = pd.Series(data=ebm.temperature[:,0], index=df_forcing.index)

    return ensemble_temperatures, ebm_tas, ensemble_ecs, ensemble_toa_imb



def get_save_temp_projections(model, cf_min=0.76, cf_max=1.72, ssp=126, seed=20250630, fair_out=FAIR_OUT,
                             erfaci_ci90=[-2.65, -0.07], erfari_ci90=[-0.71, -0.14], index=0, file_path=FILE_PATH):
    # Get the requested model parameters
    model_params = pd.read_csv(f'{file_path}/4xCO2_cummins_ebm3.csv',index_col=['model']).loc[model]

    # four models have multiple ensemble members
    if model in ["CanESM5", "CNRM-ESM2-1", "GISS-E2-1-G", "MRI-ESM2-0"]:
        model_params = model_params.iloc[index]
    
    # Read in the full ssp126 forcing to be able to predict future warming
    if ssp == 126:
        df_forcing = pd.read_csv(f'{file_path}/ERF_ssp126_1750-2500.csv', index_col='year').loc[1850:2100]
    elif ssp == 245:
        df_forcing = pd.read_csv(f'{file_path}/ERF_ssp245_1750-2500.csv', index_col='year').loc[1850:2100]
    df_forcing['aerosol'] = df_forcing['aerosol-cloud_interactions'] + df_forcing['aerosol-radiation_interactions']

    # random number generator for reproducibility
    rng = np.random.default_rng(seed=seed)

    # forcing without direct/indirect aerosol
    historical_forcing_sans_aerosol = df_forcing['total'] - df_forcing['aerosol-cloud_interactions'] - df_forcing['aerosol-radiation_interactions']

    # get & scale ERFaci and ERFari
    erfaci = get_pdf90(lower=erfaci_ci90[0], upper=erfaci_ci90[1], rng=rng) 
    erfaci_df = pd.DataFrame(erfaci, columns=['ERFaci'])
    erfari = get_pdf90(lower=erfari_ci90[0], upper=erfari_ci90[1], rng=rng)
    erfari_df = pd.DataFrame(erfari, columns=['ERFari'])
    erfaci_scaled = scale_aci_forcing(erfaci_df, df_forcing=df_forcing).ERFaci
    erfari_scaled = scale_ari_forcing(erfari_df, df_forcing=df_forcing).ERFari

    # climate feedback
    climate_feedback = get_pdf90(lower=cf_min, upper=cf_max, rng=rng)
    climate_feedback_df = pd.DataFrame(climate_feedback, columns=['climate_feedback'])


    # get AR6 temeperature line using these model parameters (vs. modifying the climate feedback param)
    ebm3 = EnergyBalanceModel(
        ocean_heat_capacity=[model_params.C1, model_params.C2, model_params.C3],
        ocean_heat_transfer=[model_params.kappa1, model_params.kappa2, model_params.kappa2],
        deep_ocean_efficacy=model_params.epsilon,  
        gamma_autocorrelation=model_params.gamma,  
        sigma_xi=model_params.sigma_xi,
        sigma_eta=model_params.sigma_eta,
        forcing_4co2=model_params.F_4xCO2,
        stochastic_run=False,
        seed=16
    )
    ebm3.add_forcing(forcing = df_forcing['total'].values, timestep=1)
    ebm3.run()
    ar6_tas = pd.Series(data=ebm3.temperature[:,0], index=df_forcing.index)

    # get projected temperatures
    proj_temps, temp2, ecs, toa_imb = calc_temperatures(climate_feedback_df, erfaci_scaled, erfari_scaled, n_samples=len(erfaci_scaled),
                                                 historical_forcing_sans_aerosol=historical_forcing_sans_aerosol, df_forcing=df_forcing, model_params=model_params)


    # save files
    erfaci_scaled = erfaci_scaled.rename({"index": "ensemble"})
    erfari_scaled = erfari_scaled.rename({"index": "ensemble"})
    da_ar6_tas = ar6_tas.to_xarray()
    cf_da = climate_feedback_df.to_xarray()["climate_feedback"]
    cf_da = cf_da.rename({"index": "ensemble"})
    erfaci_da = xr.DataArray(erfaci, dims=["ensemble"], coords={"ensemble": erfaci_scaled.ensemble}, name="ERFaci")
    erfari_da = xr.DataArray(erfari, dims=["ensemble"], coords={"ensemble": erfari_scaled.ensemble}, name="ERFari")

    ds = xr.Dataset({
        "temps": proj_temps,
        "ERFaci": erfaci_da,
        "ERFari": erfari_da,
        "ERFaci_scaled": erfaci_scaled,
        "ERFari_scaled": erfari_scaled,
        "climate_feedback": cf_da,
        "AR6_tas": da_ar6_tas,
        "ECS": ecs,
        "TOA_energy_imbalance": toa_imb
    })
    if index is not None:
        model_lab = f"{model}__{index}"
    else:
        model_lab = model
    ds.attrs = {"SSP": ssp, "model": model}
    ds.to_netcdf(fair_out + f"{model_lab}__SSP{ssp}_temp_projections.nc")


    # quick calculations
    dTh = proj_temps.sel(year=2000) - proj_temps.sel(year=1860)
    before = proj_temps.sel(year=slice(1850, 1900)).mean(dim="year")
    after = proj_temps.sel(year=slice(2081, 2100)).mean(dim="year")
    dTf = after - before
    dTh_da = xr.DataArray(dTh, dims=["ensemble"], coords={"ensemble": proj_temps.ensemble})
    dTf_da = xr.DataArray(dTf, dims=["ensemble"], coords={"ensemble": proj_temps.ensemble})

    # quick scatterplot
    erfaer = erfaci_da + erfari_da
    plt.scatter(dTh_da.sortby(dTf_da), erfaer.sortby(dTf_da), c=dTf.sortby(dTf_da),  cmap="Spectral_r", alpha=0.75, vmin=-.3, vmax=6)
    plt.axhline(-1, color="C0")
    plt.axvline(0.6, color="C0")
    plt.axvline(0, color="gray", ls=":")
    plt.axvline(1.4, color="gray", ls=":")
    plt.axhline(-1.8, color="gray", ls=":")
    plt.axhline(-0.3, color="gray", ls=":")
    plt.title(model)
    plt.colorbar()
    plt.show()
    
    return ds


