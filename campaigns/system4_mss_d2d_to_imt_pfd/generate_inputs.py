from itertools import product
from pathlib import Path
from copy import deepcopy, copy
from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
import argparse
from time import time
from campaigns.system4_mss_d2d_to_imt_pfd.constants import (
    CAMPAIGN_STR,
    CAMPAIGN_NAME,
    INPUTS_DIR,
    IMT_UE_TYPE,
    MSS_D2D_LOAD_FACTOR,
    IMT_A5_DL_BAND_LOW_MHZ,
    IMT_B4_DL_BAND_LOW_MHZ,
    get_specific_pattern
)

# SEED = int(time() * 1000) % 2**32 - 1
SEED = 69
NUM_SNAPSHOTS = int(1e4)

# Parameters for analysis
# beam_power_backoff_dB = 5.0  # dB
# min_beam_ground_elev_deg = 38.0  # degrees
minimum_elevation_from_es = 5.0  # degrees

general = {
    "seed": SEED,
    "num_snapshots": NUM_SNAPSHOTS,
    "overwrite_output": False,
    "output_dir": "to-update",
    "output_dir_prefix": "to-update",
    "system": "MSS_D2D",
    "imt_link": "DOWNLINK",
}

# Generate the parameters for the UE vs CPE campaign
#
# Assumptions for CPE parameters:
# antenna height = 1.5 m
# body loss = 0 dB
# antenna gain = 0 dBi

def generate_inputs(band_mhz=700):
    """Generate the YAML parameters files for the campaign.
    band_mhz: Frequency band in MHz (700 or 2100)"""

    if band_mhz not in [700, 2100]:
        raise ValueError("band_mhz must be 700 or 2100")

    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Generating files in: {INPUTS_DIR}")
    factory = ParametersFactory()

    # Band specific settings
    if band_mhz == 700:
        print("Generating inputs for 700 MHz band...")
        imt_id = "imt.upto-1GHz.single-bs.urban-macro-bs"
        mss_id = "system-4.698-960MHz-block2.690km-antenna-update"
        # exclusion_margins_km = [30]
        # exclusion_margins_km = [28]
        # imt_bandwidth_mhz = 10.0
        imt_bandwidth_mhz = 5.0
        imt_frequency_mhz = IMT_A5_DL_BAND_LOW_MHZ + imt_bandwidth_mhz / 2
    else:
        print("Generating inputs for 2100 MHz band...")
        imt_id = "imt.1-3GHz.single-bs.aas-macro-bs"
        mss_id = "system-4.2110-2200MHz.690km"
        # exclusion_margins_km = [24, 36, 48]
        imt_bandwidth_mhz = 20.0
        imt_frequency_mhz = IMT_B4_DL_BAND_LOW_MHZ + imt_bandwidth_mhz / 2

    ##############################################
    # Campaign parameters!
    pwr_ctrl_zone_margin_from_border = 150.  # km
    min_beam_ground_elevs_deg = [20, 30, 45, 70, 80]
    exclusion_margins_km = [30]
    power_backoffs = [0.0, 10.0, 15.0]
    load_factors = [0.2, 0.5]
    propagation_models = ["P619"]
    ##############################################

    scenario_params = [
        IMT_UE_TYPE,
        [imt_id],
        [mss_id],
        min_beam_ground_elevs_deg,
        exclusion_margins_km,
        power_backoffs,  # power backoff dB
        load_factors,
        propagation_models,
    ]

    total_files = 0
    for (
        imt_ue_type,
        imt_id,
        mss_d2d_id,
        beam_elev,
        exclusion_margin_km,
        pwr_boff,
        lf,
        prop,
    ) in product(*scenario_params):

        general["imt_link"] = 'DOWNLINK'  # only downlink for UE/CPE

        print("Generating parameters:")
        print("\timt_link =", general["imt_link"])
        print("\timt_ue_type =", imt_ue_type)
        print("\timt_id =", imt_id)
        print("\tmss_d2d_id =", mss_d2d_id)
        print("\tbeam elev =", beam_elev)
        print("\texclusion margin =", exclusion_margin_km)

        params = (
            factory
            .load_from_id(imt_id)
            .load_from_id(mss_d2d_id)
            .load_from_dict({"general": general})
            .build()
        )

        # Scenario configuration
        params.general.enable_adjacent_channel = True
        params.general.enable_cochannel = True
        params.general.output_dir = f"{CAMPAIGN_STR}/output_{band_mhz}/"
        params.imt.interfered_with = True
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        # Parameters for oob-emissions inside IMT band
        params.imt.adjacent_ch_reception = "OFF"
        params.mss_d2d.adjacent_ch_emissions = "ACLR"
        params.mss_d2d.adjacent_ch_leak_ratio = 45.0  # dB - AST typical first adjacent band


        # IMT UE parameters
        params.imt.ue.distribution_distance = "SQRT(UNIFORM)"
        params.imt.ue.antenna.pattern = "OMNI"
        params.imt.ue.antenna.gain = -3.0
        # params.imt.ue.k = 3  # single user per cell
        params.imt.ue.k = 1  # single user per cell
        # CPE-speficic parameters
        if imt_ue_type == "imt-cpe":
            params.imt.ue.body_loss = 0.0
            params.imt.ue.antenna.gain = 0.0
            params.imt.ue.height = 1.5
            params.imt.ue.ohmic_loss = 2.0  # tipical cable and other losses @700MHz
            params.imt.ue.indoor_percent = 0.0  # all outdoor

        # Frequencies and bandwidths
        params.imt.bandwidth = imt_bandwidth_mhz
        params.imt.frequency = imt_frequency_mhz
        params.imt.guard_band_ratio = 0.1  # 10% guard band - single UE has 4.5MHz usable bw in 5MHz channel
        params.mss_d2d.bandwidth = 5.0  # MHz
        params.mss_d2d.frequency = params.imt.frequency  # full bw overlap

        # Adding this just to prevent UserWarnings for unset mask parameters.
        params.mss_d2d.spectral_mask = "MSS"

        # Parameters used for P.619
        # WARNING: Remember to set the lut in propagation/Dataset
        params.mss_d2d.channel_model = prop
        params.mss_d2d.param_p619.earth_station_lat_deg = -25.5549751
        params.mss_d2d.param_p619.earth_station_alt_m = 200
        params.mss_d2d.param_p619.mean_clutter_height = "low"

        if prop == "P619":
            # P.619 suggests 3dB polarization loss as good constant value for monte carlo
            params.mss_d2d.polarization_loss = 3.0  # dB
        else:
            params.mss_d2d.polarization_loss = 0.0  # dB

        # Geometry
        # International Friendship Bridge
        center_lat = -25.5549751
        center_lon = -54.5746686
        params.imt.topology.central_latitude = center_lat
        params.imt.topology.central_longitude = center_lon
        params.imt.topology.central_altitude = 200

        # Beam management - service grid
        params.mss_d2d.cell_radius = 24e3
        params.mss_d2d.beams_load_factor = lf
        params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
        params.mss_d2d.beam_positioning.service_grid.transform_grid_randomly = True
        service_grid = params.mss_d2d.beam_positioning.service_grid
        service_grid.grid_in_zone.type = "FROM_COUNTRIES"
        service_grid.grid_in_zone.from_countries.country_names = [
            "Brazil",
        ]
        service_grid.grid_in_zone.from_countries.margin_from_border = exclusion_margin_km

        # Satellite activity conditions
        params.mss_d2d.sat_is_active_if.conditions = [
            "MINIMUM_ELEVATION_FROM_ES",
            "LAT_LONG_INSIDE_COUNTRY"
        ]
        params.mss_d2d.sat_is_active_if.lat_long_inside_country.country_names = [
            "Brazil",
        ]
        params.mss_d2d.sat_is_active_if.minimum_elevation_from_es = minimum_elevation_from_es
        # big number to make it so any visible satellite is ellegible
        service_grid.eligible_sats_margin_from_border = -200.0
        # This parameter define the minium elevation angle for the service grid points
        service_grid.minimum_service_angle = beam_elev

        # AST's specific parameters
        # params.mss_d2d.antenna.pattern = "Antenna System 4"
        params.mss_d2d.antenna.pattern = "ARRAY System 4"
        params.mss_d2d.antenna.array.element_max_g = 4.86
        params.mss_d2d.antenna.array.n_rows = 80
        params.mss_d2d.antenna.array.n_columns = 96
        params.mss_d2d.antenna.array.element_horiz_spacing = 0.5
        params.mss_d2d.antenna.array.element_vert_spacing = 0.5
        params.mss_d2d.antenna.array.element_pattern = "FIXED"

        zones = params.mss_d2d.power_control_zones.zones
        # km
        zones[0].geometry.from_countries.country_names = \
            deepcopy(service_grid.grid_in_zone.from_countries.country_names)
        zones[0].geometry.from_countries.margin_from_border = pwr_ctrl_zone_margin_from_border
        # no power backoff on most of the country
        zones[0].power_backoff_db = 0.
        # backoff on 0 to 100km margin from border
        zones[1].geometry.from_countries.country_names = \
            deepcopy(service_grid.grid_in_zone.from_countries.country_names)
        zones[1].geometry.from_countries.margin_from_border = 0
        zones[1].power_backoff_db = pwr_boff

        # service_grid.grid_in_zone.type = "CIRCLE"
        # service_grid.grid_in_zone.circle.center_lat = center_lat
        # service_grid.grid_in_zone.circle.center_lon = center_lon
        # # grid_radius = float(get_service_zone_radius_from_max_num_of_beams(
        # #     max_n_beams, CELL_RADIUS_KM, exclusion_margin_km
        # # ))
        # # print("grid_radius", grid_radius)
        # service_grid.grid_in_zone.circle.radius_km = 120

        # service_grid.grid_exclusion_zone.type = "FROM_COUNTRIES"
        # service_grid.grid_exclusion_zone.from_countries.country_names = ["Paraguay"]
        # service_grid.grid_exclusion_zone.from_countries.margin_from_border = -exclusion_margin_km

        # Generate the filename pattern
        specific = get_specific_pattern(
            imt_ue_type, imt_id, mss_d2d_id, beam_elev, exclusion_margin_km, pwr_boff, lf, prop
        )

        params.general.output_dir_prefix = OUTPUT_START_NAME + specific
        # readable = get_readable_from_str(params.general.output_dir_prefix)
        # print("readable", readable)

        output_path = INPUTS_DIR / f"{PARAMETER_START_NAME}{specific}.yaml"

        # Write YAML
        try:
            dump_parameters(output_path, params)
            print(f"Generated parameter file: {output_path}")
            total_files += 1
        except Exception as e:
            print(f"Parameter generation failed {output_path}: {str(e)}")

    print(f"\nTotal generated files: {total_files}\n")


def clear_inputs():
    """Clear the input directory before generation"""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Clearing directory: {INPUTS_DIR}")
    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate simulation inputs')
    parser.add_argument('--band_mhz', type=int, choices=[700, 2100], default=700,
                        help='Frequency band in MHz (700 or 2100)')
    parser.add_argument('--dont-clear', action='store_true', default=False,
                        help='Skip clearing the inputs directory')
    args = parser.parse_args()

    if not args.dont_clear:
        clear_inputs()
    generate_inputs(band_mhz=args.band_mhz)
