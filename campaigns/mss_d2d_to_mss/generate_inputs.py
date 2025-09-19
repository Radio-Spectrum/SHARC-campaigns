from itertools import product
import numpy as np
from pathlib import Path

from sharc.parameters.antenna.parameters_antenna_s1528 import ParametersAntennaS1528
from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.mss_d2d_to_mss.constants import (
    CAMPAIGN_STR, CAMPAIGN_NAME, INPUTS_DIR,
    IMT_MSS_DC_IDS, MSS_DC_LOAD_FACTORS, SINGLE_ES_MSS_IDS,
    get_specific_pattern
)

INPUTS_DIR = Path(INPUTS_DIR)

SEED = 82

general = {
    "seed": SEED,
    "num_snapshots": 1000,
    "overwrite_output": False,
    "output_dir": f"{CAMPAIGN_STR}/output/",
    "output_dir_prefix": "to-update",
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "DOWNLINK",
}


def get_taylor_cell_radius(
    params_s1528: ParametersAntennaS1528,
    sat_alt_km: float,
    attempt_max_angle: float = 10.0,
    attempt_resolution: int = int(1e6)
):
    antenna = AntennaS1528Taylor(
        params_s1528
    )
    off_axis = np.linspace(0, attempt_max_angle, attempt_resolution)
    gains = antenna.calculate_gain(
        off_axis_angle_vec=off_axis,
        # theta is set to 0 since it makes no difference
        # when antenna pattern is circular
        theta_vec=0,
    )
    angle_7dB_i = np.where(gains <= params_s1528.antenna_gain - 7)[0][0]
    angle_7dB = off_axis[angle_7dB_i]
    cell_radius = np.tan(np.deg2rad(angle_7dB)) * sat_alt_km * 1e3

    return int(cell_radius)


def calculate_equivalent_acs(
    ue_f_MHz,
    ue_bw_MHz,
    other_f_MHz,
    other_bw_MHz,
):
    """
    Returns the equivalent ACS considering the freqs and bws
    """
    # NOTE: this function probably should not be here, but somehow
    # together with from-docs equipment definition

    ue_lim_s = ue_f_MHz - ue_bw_MHz / 2
    ue_lim_e = ue_f_MHz + ue_bw_MHz / 2
    other_lim_s = other_f_MHz - other_bw_MHz / 2
    other_lim_e = other_f_MHz + other_bw_MHz / 2

    if (
        ue_lim_s < other_lim_s < ue_lim_e
    ) or (
        ue_lim_s < other_lim_e < ue_lim_e
    ):
        raise ValueError(
            "Expected adjacent channel to calculate for ACS"
        )
    if other_lim_s >= ue_lim_e:
        df_s = other_lim_s - ue_lim_e
        df_e = other_lim_e - ue_lim_e
    elif other_lim_e <= ue_lim_s:
        df_s = ue_lim_s - other_lim_e
        df_e = ue_lim_s - other_lim_s

    mask_lims = np.array([
        0.,
        ue_bw_MHz,
        3 * ue_bw_MHz,
        np.inf,
    ])
    mask_vals_dBc = np.array([
        15., 25., 30.
    ])

    mask_bins_overlap_MHz = np.zeros_like(mask_vals_dBc)
    for i in range(len(mask_lims) - 1):
        win_s = max(mask_lims[i], df_s)
        win_e = min(mask_lims[i + 1], df_e)
        mask_bins_overlap_MHz[i] = max(win_e - win_s, 0)

    equivalent_attenuation = -10 * np.log10(
        np.sum(mask_bins_overlap_MHz * 10 ** (-0.1 * mask_vals_dBc))
        / other_bw_MHz
    )

    return float(equivalent_attenuation)


def test_calculate_equivalent_acs():
    """
    Tests and plots mask calculation for this system acs
    """
    # NOTE: this function probably should not be here, but somehow
    # together with from-docs equipment definition
    acs = calculate_equivalent_acs(
        2500 - 1.23/2, 1.23,
        2500 + 1.23/2, 1.23,
    )

    if abs(acs - 15) > 1e-5:
        raise Exception(f"{acs} != 15")

    acs = calculate_equivalent_acs(
        2500 - 1.23/2, 1.23,
        2500 + 1.23/2 + 1.23, 1.23,
    )

    if abs(acs - 25) > 1e-5:
        raise Exception(f"{acs} != 25")

    acs = calculate_equivalent_acs(
        2500 - 1.23/2, 1.23,
        2500 + 5/2, 5,
    )

    if abs(acs - 20.1786252944) > 1e-5:
        raise Exception(f"{acs} != 20.1786252944")


def generate_inputs():
    """Generates all campaign input files"""
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Generating input parameters at:\n\t{INPUTS_DIR}")
    factory = ParametersFactory()
    total = 0

    imt_freq_power_map = {
        2147.5: 14.008,
        2152.5: 24.028,
        2157.5: 42.048
    }

    for imt_id, single_es_id in product(IMT_MSS_DC_IDS, SINGLE_ES_MSS_IDS):
        print(f"[Building params for {imt_id} -> {single_es_id}]")

        params = factory.load_from_id(
            imt_id
        ).load_from_id(
            single_es_id
        ).load_from_dict(
            {"general": general}
        ).build()

        params.general.enable_adjacent_channel = True
        params.general.enable_cochannel = False
        params.imt.interfered_with = False
        # NOTE: needed for performance. Discards unnecessary calcs.
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        params.imt.adjacent_ch_emissions = "ACLR"
        # We set this as the EIRP value already includes the adjacent emissions
        params.imt.bs.adjacent_ch_leak_ratio = 0

        params.single_earth_station.adjacent_ch_reception = "ACS"
        params.single_earth_station.frequency = 2160 + params.single_earth_station.bandwidth

        # Refernce latitude and longitude taken from Cuiaba station
        params.imt.topology.central_latitude = -15.3300
        params.imt.topology.central_longitude = -56.0400
        params.imt.topology.central_altitude = 165

        params.single_earth_station.season = "SUMMER"
        params.single_earth_station.channel_model = "P619"
        # 3dB polarization loss, as suggested by P.619
        params.single_earth_station.polarization_loss = 3

        params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
        params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude
        # NOTE: we chose rural/low cluttered environment since MSS UEs are normally there
        params.single_earth_station.param_p619.mean_clutter_height = "low"
        params.single_earth_station.param_p619.below_rooftop = 0

        # position ES at reference
        es_geom = params.single_earth_station.geometry
        es_geom.location.type = "FIXED"
        es_geom.location.fixed.x = 0
        es_geom.location.fixed.y = 0

        es_geom.azimuth.type = "UNIFORM_DIST"
        es_geom.azimuth.uniform_dist.max = 180.
        es_geom.azimuth.uniform_dist.min = -180.

        es_geom.elevation.type = "UNIFORM_DIST"
        es_geom.elevation.uniform_dist.max = 90.
        es_geom.elevation.uniform_dist.min = 5.

        params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
        params.imt.topology.mss_dc.beam_positioning.service_grid.transform_grid_randomly = True
        country_list = [
            "Brazil", "Argentina", "Bolivia", "Chile", "Peru", "Paraguay", "Uruguay"
        ]
        params.imt.topology.mss_dc.beam_positioning.service_grid.country_names = country_list

        # this is distance in km so that actual best satellite is used for each grid point
        angle_dist_between_planes = 360 / \
            params.imt.topology.mss_dc.orbits[0].n_planes
        margin = -np.ceil((angle_dist_between_planes / 2) * 111)
        params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = int(
            margin)

        # Beam is active if satellite
        params.imt.topology.mss_dc.sat_is_active_if.conditions = [
            "LAT_LONG_INSIDE_COUNTRY",
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        params.imt.topology.mss_dc.sat_is_active_if.lat_long_inside_country.country_names = country_list
        params.imt.topology.mss_dc.sat_is_active_if.lat_long_inside_country.margin_from_border = \
            params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border

        # Get cell radius based on co-channel antenna pattern
        params.imt.bs.antenna.itu_r_s_1528.frequency = 2000
        params.imt.bs.antenna.set_external_parameters(
            frequency=2000,
        )
        params.imt.topology.mss_dc.beam_radius = get_taylor_cell_radius(
            params.imt.bs.antenna.itu_r_s_1528,
            params.imt.topology.mss_dc.orbits[0].apogee_alt_km,
        )
        print(
            f"\tA cell radius of {params.imt.topology.mss_dc.beam_radius} will be used for MSS DC")

        params.imt.bs.antenna.pattern = "MSS Adjacent"

        # also do uniform dist of elevation angles
        params.single_earth_station.geometry.elevation.type = "UNIFORM_DIST"
        params.single_earth_station.geometry.elevation.uniform_dist.min = 10.
        params.single_earth_station.geometry.elevation.uniform_dist.max = 90.

        for mss_dc_load, imt_freq in product(MSS_DC_LOAD_FACTORS, imt_freq_power_map.keys()):
            params.imt.frequency = imt_freq
            params.imt.bs.conducted_power = imt_freq_power_map[imt_freq]
            params.imt.bs.load_probability = mss_dc_load

            params.imt.bs.antenna.mss_adjacent.frequency = imt_freq
            params.imt.bs.antenna.set_external_parameters(
                frequency=imt_freq,
            )

            base_specific = get_specific_pattern(
                imt_id, single_es_id, mss_dc_load
            )
            specific = f"{base_specific}_freq{imt_freq}"

            params.general.output_dir_prefix = OUTPUT_START_NAME + specific

            dump_parameters(
                INPUTS_DIR / (PARAMETER_START_NAME + specific + ".yaml"),
                params,
            )
            total += 1

    print(f"\nFiles generated on this run: {total}\n")
    if INPUTS_DIR.exists():
        n_of_inputs = len(list(INPUTS_DIR.glob("*.yaml")))
        print("Total number of input files: ", n_of_inputs)


def clear_inputs():
    """Removes all current inputs in inputs directory"""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Clearing inputs from dir '{INPUTS_DIR}'")

    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()


if __name__ == "__main__":
    # test_calculate_equivalent_acs()
    clear_inputs()
    generate_inputs()