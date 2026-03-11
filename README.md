# multi-model-ppe-2026
Code used in Nugent et al. (2026), in review at _Science_, on building an observationally constrained multi-model PPE to get an updated estimate of ERFaci when both structural and parametric uncertainty are taken into account. Brief descriptions of each file are included below.

Processed data files and other files needed to reproduce the figures for this paper is hosted on Dryad ([doi:10.5061/dryad.rbnzs7hr0](https://doi.org/10.5061/dryad.rbnzs7hr0)). Notebooks for processing the original PPE/CMIP6 files are included here, but the unprocessed files are omitted from the data repository due to size constraints. More information on how to access the original/unprocessed files is provided in the README for the Dryad data repository.

## Contents:
### Notebooks
#### Main Text Analysis/Figures

* [areameanvsbellouin_from_DM.ipynb](notebooks/main_text/areameanvsbellouin_from_DM.ipynb): calculate the WCRP ∆lnLWP CI from [Bellouin et al., 2020](https://doi.org/10.1029/2019RG000660)
* [fit_albedo_susceptibility.ipynb](notebooks/main_text/fit_albedo_susceptibility.ipynb): get the emergent relationship from [Song et al., 2024](https://doi.org/10.1029/2024GL108663) to calculate albedo susceptibility (da/dlwp) from PD LWP
* [mask_PPE_CMIP6_files__new_E3SM.ipynb](notebooks/main_text/mask_PPE_CMIP6_files__new_E3SM.ipynb): main notebook for data processing for the PPEs and CMIP6 models; masks land/ocean/convective regions as appropriate, regrids, and processes CMIP6 data
* [calculate_constraints__new_E3SM.ipynb](notebooks/main_text/calculate_constraints__new_E3SM.ipynb): create `.pickle` files of which ensemble members meet which constraints and calculate the best-fit lines for the constrained ensembles
* [Fig1_dLWP_ERFaci_PDLWP.ipynb](notebooks/main_text/Fig1_dLWP_ERFaci_PDLWP.ipynb): plot Figure 1
* [check_ukesm_ensn.ipynb](notebooks/main_text/check_ukesm_ensn.ipynb): find which observational constraint is not met by the UKESM1-GA7.1 ensemble member with large negative ∆LWP that does meet the PD LWP constraint
* [GPR_final_train_test_predict.ipynb](notebooks/main_text/GPR_final_train_test_predict.ipynb): main notebook for the Gaussian process regression; finds suitable kernels, calculates predicted credible intervals, and plots the validation figures
* [Fig2_constrained_ranges.ipynb](notebooks/main_text/Fig2_constrained_ranges.ipynb): plot Figure 2
* [FaIR_projections_SSP1-2.6.ipynb](notebooks/main_text/FaIR_projections_SSP1-2.6.ipynb): generate the FaIR projections for SSP1-2.6 using CMIP6 model parameters and plot Figure 3

#### Supplementary Analysis/Figures
* [FaIR_projections_SSP2-4.5.ipynb](notebooks/supplementary_and_summary/FaIR_projections_SSP2-4.5.ipynb): generate the FaIR projections for SSP2-4.5 using CMIP6 model parameters and plot Figure S8
* [final_GPR_sensitivity.ipynb](notebooks/supplementary_and_summary/final_GPR_sensitivity.ipynb): perform the leave-one-out sensitivity tests for the GP regression and save the predicted credible intervals
* [FigS1_ens_constraints.ipynb](notebooks/supplementary_and_summary/FigS1_ens_constraints.ipynb): plot Figure S1
* [FigS6_spatial_plots.ipynb](notebooks/supplementary_and_summary/FigS6_spatial_plots.ipynb): plot Figure S6
* [FigS7_AOD_PI.ipynb](notebooks/supplementary_and_summary/FigS7_AOD_PI.ipynb): plot Figure S7
* [test_FaIR.ipynb](notebooks/supplementary_and_summary/test_FaIR.ipynb): test constraining the FaIR projections with alternate time periods for GMST anomalies - using the one from [Watson-Parris, 2025](https://doi.org/10.1029/2024GL114269)

#### Summary Figure
* [get_MAC-LWP_for_fig.ipynb](notebooks/supplementary_and_summary/get_MAC-LWP_for_fig.ipynb): calculate annual mean observed liquid water path for the summary figure
* [summary_fig.ipynb](notebooks/supplementary_and_summary/summary_fig.ipynb): plot the summary figure included with the 1-page structured abstract

### Python Scripts
* [e3sm_util.py](python_scripts/e3sm_util.py): helper functions for handling the E3SMv3 unstructured grid
* [fair_projections.py](python_scripts/fair_projections.py): code to run the FaIR energy balance model and generate projections
* [multi_ppe_constraint_rev.py](python_scripts/multi_ppe_constraint_rev.py): helper functions for applying the obsevational constraints

### Environments
* [ppe.yml](ppe.yml): conda virtual environment for most of the processing
* [esem-env.yml](esem-env.yml): conda virtual environment to run FaIR (`FaIR_projections_SSP*.ipynb`)
* [xesmf_env.yml](xesmf_env.yml): conda virtual environment to use xesmf regridding (`mask_PPE_CMIP6_files__new_E3SM.ipynb`)

### Figures
* [figures/](figures/): Figs. 1-3; Figs. S1-S8; summary figure (Fig. 0)

## References for FaIR:
* FaIR documentation: https://docs.fairmodel.net/en/latest/index.html
* FaIR publications:
   * Leach, N. J., Jenkins, S., Nicholls, Z., Smith, C. J., Lynch, J., Cain, M., Walsh, T., Wu, B., Tsutsui, J., and Allen, M. R.: FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration, Geosci. Model Dev., 14, 3007--3036, https://doi.org/10.5194/gmd-14-3007-2021, 2021
   * Smith, C. J., Forster, P. M., Allen, M., Leach, N., Millar, R. J., Passerello, G. A., and Regayre, L. A.: FAIR v1.3: A simple emissions-based impulse response and carbon cycle model, Geosci. Model Dev., https://doi.org/10.5194/gmd-11-2273-2018, 2018.
