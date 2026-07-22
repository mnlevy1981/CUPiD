#!/usr/bin/env python3
from __future__ import annotations

# import shutil

import click

# import yaml

try:
    import util
except ModuleNotFoundError:
    import cupid.util as util


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def validate_config(config_path="config.yml"):
    control = util.get_control_dict(config_path)

    check_global_params(control)
    check_timeseries_params(control)
    check_compute_notebooks_params(control)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    "config_path",
    required=False,
    default="config.yml",
)
def check_consistency(config_path):
    validate_config(config_path)


def check_global_params(control):
    global_params = control["global_params"]

    required_global_lists = [
        "case_names",
        "case_nicknames",
        "start_dates",
        "end_dates",
        "climo_start_years",
        "climo_end_years",
        "CESM_output_dir",
    ]

    for key in required_global_lists:
        if key not in global_params:
            raise click.ClickException(
                f"{key} must be included under global_params in config file.",
            )
        if not isinstance(global_params[key], list):
            raise click.ClickException(
                f"global_params.{key} must be a list in config file.",
            )

    lengths = [len(global_params[key]) for key in required_global_lists]

    if len(set(lengths)) != 1:
        length_summary = "\n".join(
            f"  {key}: {length}" for key, length in zip(required_global_lists, lengths)
        )

        raise click.ClickException(
            "The global_params entries in config file must all have the same length:\n"
            f"{length_summary}",
        )


def check_timeseries_params(control):
    timeseries_params = control["timeseries"]
    case_names = control["global_params"]["case_names"]

    components = ["atm", "lnd", "ocn", "ice", "glc", "rof"]

    required_component_param_lists = ["start_years", "end_years"]

    required_timeseries_lists = ["ts_done", "overwrite_ts"]

    for param in required_timeseries_lists:
        if not isinstance(timeseries_params[param], list):
            raise click.ClickException(
                "timeseries entries in config file for 'ts_done' and"
                " 'overwrite_ts' should be a list matching the length of case_names.",
            )

    for component in components:
        for param in required_component_param_lists:
            if not isinstance(timeseries_params[component][param], list):
                raise click.ClickException(
                    "timeseries entries in config file for 'start_years' and 'end_years' for each component"
                    "(atm, lnd, ocn, ice, glc, rof) should be a list matching the length of case_names.",
                )

    comp_lengths = []
    ts_lengths = []
    for component in components:
        for param in required_component_param_lists:
            comp_lengths.append(len(timeseries_params[component][param]))
    for param in required_timeseries_lists:
        ts_lengths.append(len(timeseries_params[param]))

    comp_error_msg = (
        "The timeseries entries in config file for 'start_years' and 'end_years' "
        "for each component (atm, lnd, ocn, ice, glc, rof) must have "
        "the same length and match the length of case_names."
    )
    ts_error_msg = (
        "The timeseries entries in config file for 'ts_done' and 'overwrite_ts' "
        "must have the same length and match the length of case_names."
    )

    if len(set(comp_lengths)) != 1 or comp_lengths[0] != len(case_names):
        raise click.ClickException(comp_error_msg)

    if len(set(ts_lengths)) != 1 or ts_lengths[0] != len(case_names):
        raise click.ClickException(ts_error_msg)

    if "ts_output_dir" in timeseries_params:
        if not isinstance(timeseries_params["ts_output_dir"], (list, str, type(None))):
            raise click.ClickException(
                "ts_output_dir in config file must be a string or a list.",
            )
        if isinstance(timeseries_params["ts_output_dir"], list):
            if len(timeseries_params["ts_output_dir"]) != len(case_names):
                raise click.ClickException(
                    "ts_output_dir in config file must be the same length as case_names.",
                )


def check_compute_notebooks_params(control):
    compute_notebooks_params = control["compute_notebooks"]
    case_names = control["global_params"]["case_names"]

    gauge_grid_name = compute_notebooks_params["rof"][
        "global_discharge_gauge_compare_obs"
    ]["parameter_groups"]["none"]["grid_name"]
    ocean_grid_name = compute_notebooks_params["rof"][
        "global_discharge_ocean_compare_obs"
    ]["parameter_groups"]["none"]["grid_name"]
    atm_regrid = compute_notebooks_params["atm"]["Global_PSL_NMSE_compare_obs_lens"][
        "parameter_groups"
    ]["none"]["regridded_output"]
    atm_ADF_regrid = compute_notebooks_params["atm"]["ADF"]["external_tool"][
        "regridded_output"
    ]
    ldf_regrid = compute_notebooks_params["lnd"]["LDF"]["external_tool"][
        "regridded_output"
    ]

    required_compute_notebooks_lists = [
        gauge_grid_name,
        ocean_grid_name,
        atm_regrid,
        atm_ADF_regrid,
        ldf_regrid,
    ]

    lengths = []
    error_msg = (
        "compute_notebooks entries in config file must all have the same length "
        "for 'grid_name' and 'regridded_output' (atm) to match the length "
        "of case_names."
    )

    for param in required_compute_notebooks_lists:
        if param != ldf_regrid:
            if isinstance(param, (str, bool)):
                raise click.ClickException(
                    "'grid_name' and 'regridded_output' (atm) entry "
                    "in config file under 'compute_notebooks' should "
                    "be a list matching the length of case_names.",
                )
            else:
                lengths.append(len(param))
        else:
            if isinstance(param, (str, bool)):
                raise click.ClickException(
                    "'regridded_output' (lnd) entry in config file "
                    "under 'compute_notebooks' should be a list "
                    "either of length 2 or matching the length of case_names.",
                )
            if isinstance(param, (list)):
                if len(param) not in (2, len(case_names)):
                    raise click.ClickException(
                        "'regridded_output' (lnd) in config file under "
                        "'compute_notebooks' should be a list either "
                        "of length 2 or matching the length of case_names.",
                    )

    if len(set(lengths)) != 1 or lengths[0] != len(case_names):
        raise click.ClickException(error_msg)


if __name__ == "__main__":
    check_consistency()
