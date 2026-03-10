# multi-model-ppe-2026
Code used in Nugent et al. (2026), in review at _Science_, on building an observationally constrained multi-model PPE to get an updated estimate of ERFaci when both structural and parametric uncertainty are taken into account. Brief descriptions of each file are included below.

Processed data files for this paper can be found at (**TODO: put the Zotero link**). Notebooks for processing the original PPE/CMIP6 files are included here, but the unprocessed files are omitted from the data repository due to size constraints. 

## Contents:
### Notebooks
#### Main Text Analysis/Figures

* [areameanvsbellouin_from_DM.ipynb](): calculate the WCRP ∆lnLWP CI from [Bellouin et al., 2020](https://doi.org/10.1029/2019RG000660)
* [mask_PPE_CMIP6_files__new_E3SM.ipynb](): main notebook for data processing for the PPEs and CMIP6 models; masks land/ocean/convective regions as appropriate, regrids, and processes CMIP6 data
* [calculate_constraints__new_E3SM.ipynb](): create `.pickle` files of which ensemble members meet which constraints and calculate the best-fit lines for the constrained ensembles
* [Fig1_dLWP_ERFaci_PDLWP.ipynb](): plot Figure 1
* [check_ukesm_ensn.ipynb](): find which observational constraint is not met by the UKESM1-GA7.1 ensemble member with large negative ∆LWP that does meet the PD LWP constraint
* [GPR_final_train_test_predict.ipynb](): main notebook for the Gaussian process regression; finds suitable kernels, calculates predicted credible intervals, and plots the validation figures
* [Fig2_constrained_ranges.ipynb](): plot Figure 2
* [FaIR_projections_SSP1-2.6](): generate the FaIR projections for SSP1-2.6 using CMIP6 model parameters and plot Figure 3

#### Supplementary Analysis/Figures
* [FaIR_projections_SSP2-4.5.ipynb](): generate the FaIR projections for SSP2-4.5 using CMIP6 model parameters and plot Figure S8
* [final_GPR_sensitivity.ipynb](): perform the leave-one-out sensitivity tests for the GP regression and save the predicted credible intervals
* [FigS1_ens_constraints.ipynb](): plot Figure S1
* [FigS6_spatial_plots.ipynb](): plot Figure S6
* [test_FaIR.ipynb](): test constraining the FaIR projections by alternate time periods

#### Summary Figure
* [get_MAC-LWP_for_fig.ipynb](): calculate annual mean observed liquid water path for the summary figure
* [summary_fig.ipynb](): plot the summary figure included with the 1-page structured abstract

### Python Scripts
* [e3sm_util.py](): helper functions for handling the E3SMv3 unstructured grid
* [fair_projections.py](): code to run the FaIR energy balance model and generate projections
* [multi_ppe_constraint_rev.py](): helper functions for applying the obsevational constraints

### Environments
* [ppe.yml](): conda virtual environment for most of the processing
* [esem-env.yml](): conda virtual environment to run FaIR (`FaIR_projections_SSP*.ipynb`)
* [xesmf_env.yml](): conda virtual environment to use xesmf regridding (`mask_PPE_CMIP6_files__new_E3SM.ipynb`)

### Figures
* [figures/](): Figs. 1-3; Figs. S1-S8; summary figure

## References for FaIR:
* FaIR documentation: https://docs.fairmodel.net/en/latest/index.html
* ERF_ssp* files:
   * Smith, C. (2023): Chapter 7 of the Working Group I Contribution to the IPCC Sixth Assessment Report - data for Figure 7.SM.1 (v20220721). NERC EDS Centre for Environmental Data Analysis, 10 July 2023.  https://dx.doi.org/10.5285/f0f622f4e9d14f95949a5cc44451e8bb
* FaIR publications:
   * Leach, N. J., Jenkins, S., Nicholls, Z., Smith, C. J., Lynch, J., Cain, M., Walsh, T., Wu, B., Tsutsui, J., and Allen, M. R.: FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration, Geosci. Model Dev., 14, 3007--3036, https://doi.org/10.5194/gmd-14-3007-2021, 2021
   * Smith, C. J., Forster, P. M., Allen, M., Leach, N., Millar, R. J., Passerello, G. A., and Regayre, L. A.: FAIR v1.3: A simple emissions-based impulse response and carbon cycle model, Geosci. Model Dev., https://doi.org/10.5194/gmd-11-2273-2018, 2018.
