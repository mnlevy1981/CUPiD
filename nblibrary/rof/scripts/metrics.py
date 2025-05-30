from __future__ import annotations

import numpy as np

# ----- time series error
# There are many other error metrics (e.g., KGE, NSE, ame, etc.) as well as
# many flow metrics (Flow duration curve, annual maximmum flow and timing etcs.)
# available.


def remove_nan(qsim, qobs):
    """
    Compare sim array and obs array time series,
    Then remove both sim and obs at times if either or both sim and obs have NaN

    Arguments
    ---------
    qsim: array-like
        Simulated time series array.
    qobs: array-like
        Observed time series array.

    Returns
    -------
    sim_obs: float
        simulation and observation pair with nan removed
    """

    sim_obs = np.stack((qsim, qobs), axis=1)
    sim_obs = sim_obs[~np.isnan(sim_obs).any(axis=1), :]
    return sim_obs[:, 0], sim_obs[:, 1]


def corr(qsim, qobs):
    """
    Calculates pearson correlation between two flow arrays.

    Arguments
    ---------
    sim: array-like
        Simulated time series array.
    obs: array-like
        Observed time series array.

    Returns
    -------
    corr: float
        Pearson correlation between the two arrays.
    """
    qsim1, qobs1 = remove_nan(qsim, qobs)
    if qobs1.size <= 1:  # correlation cannot be computed with size 1 array
        error_metric = np.nan
    elif (
        len(np.unique(qsim1)) == 1 or len(np.unique(qobs1)) == 1
    ):  # if array has the same values, standard deviation become zero, causing "divide by zero" issue
        error_metric = np.nan
    else:
        error_metric = np.corrcoef(qsim1, qobs1)[0, 1]
    return error_metric


def pbias(qsim, qobs):
    """
    Calculates percentage bias between two flow arrays.

    Arguments
    ---------
    sim: array-like
        Simulated time series array.
    obs: array-like
        Observed time series array.

    Returns
    -------
    pbial: float
        percentage bias calculated between the two arrays.
    """
    qsim1, qobs1 = remove_nan(qsim, qobs)
    if qobs1.size == 0:
        error_metric = np.nan
    else:
        error_metric = np.sum(qsim1 - qobs1) / np.sum(qobs1) * 100
    return error_metric


def rmse(qsim, qobs):
    """
    Calculates root mean squared of error (rmse) between two time series arrays.
    Arguments
    ---------
    sim: array-like
        Simulated time series array.
    obs: array-like
        Observed time series array.

    Returns
    -------
    rmse: float
        rmse calculated between the two arrays.
    """
    qsim1, qobs1 = remove_nan(qsim, qobs)
    if qobs1.size == 0:
        error_metric = np.nan
    else:
        error_metric = np.sqrt(np.mean((qsim1 - qobs1) ** 2))
    return error_metric
