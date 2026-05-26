from itertools import product
import numpy as np
import argparse

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.mss_d2d_to_imt_macro.run import CAMPAIGN_STR, CAMPAIGN_DIR, get_output_dir_start, INPUTS_DIR
from sharc.antenna.antenna_s1528 import AntennaS1528Taylor


import yaml


POWER_CONTROL_ZONES_STR = """
  power_control_zones:
    zones:
      - power_backoff_db: 0.0
        geometry:
          type: FROM_COUNTRIES
          from_countries:
            country_names:
            - Brazil
            - Argentina
            margin_from_border: 150.0
      - power_backoff_db: 10.0
        geometry:
          type: FROM_COUNTRIES
          from_countries:
            country_names:
            - Brazil
            - Argentina
            margin_from_border: 0.0
"""
pwr_ctrl_zone_params = yaml.safe_load(POWER_CONTROL_ZONES_STR)


DC_MSS_BANDWIDTH_MHZ = 5.0
# Band configurations
# IMT frequency is set in such a way that DC-MSS is at the edge of the band for adjacent band studies
# DC-MSS-IMT band is assumed to be 5MHz
IMT_BAND_CONFIG_MAP = {
    "B1": {"lower": 698.0,  "upper": 960.0,  "typical_bw": 10.0, "imt_dl_center_f_mhz": 884.,  "imt_ul_center_f_mhz": 839. },  # 45MHz duplex spacing
    "B2": {"lower": 1427.0, "upper": 1528.0, "typical_bw": 20.0, "imt_dl_center_f_mhz": 1442., "imt_ul_center_f_mhz": 1442.},  # TDD band in Brazil
    "B3": {"lower": 1710.0, "upper": 2200.0, "typical_bw": 20.0, "imt_dl_center_f_mhz": 2125., "imt_ul_center_f_mhz": 1935.},  # 190MHz duplex spacing
    "B4": {"lower": 2300.0, "upper": 2400.0, "typical_bw": 20.0, "imt_dl_center_f_mhz": 2330., "imt_ul_center_f_mhz": 2330.},  # TDD band in Brazil
    "B5": {"lower": 2500.0, "upper": 2690.0, "typical_bw": 20.0, "imt_dl_center_f_mhz": 2635., "imt_ul_center_f_mhz": 2515.},  # 120MHz duplex spacing
}

# MSS-DC systems for simulation
DC_MSS_IDS = [
    "system-2.694MHz.698-960MHz.500km",
    "system-2.1427-1518MHz.500km",
    "system-2.1805-1920MHz.2110-2170MHz.500km",
    "system-2.2300-2400MHz.500km",
    "system-2.2500-2690MHz.500km",
    "system-3.698-960MHz.340km",
    "system-3.698-960MHz.525km",
    "system-3.2110-2200MHz.340km",
    "system-3.2110-2200MHz.525km",
    "system-3.1427-1518MHz.340km",
    "system-3.1427-1518MHz.525km",
    "system-3.2300-2690MHz.340km",
    "system-3.2300-2690MHz.525km",
    "system-4.698-960MHz.block2.690km",
    "system-4.1427-2690MHz.690km",
]

BAND_TO_DC_MSS_ID_MAP = {
    "B1": ["system-2.694MHz.698-960MHz.500km", "system-3.698-960MHz.340km",
           "system-3.698-960MHz.525km", "system-4.698-960MHz.block2.690km"],
    "B2": ["system-2.1427-1518MHz.500km", "system-3.1427-1518MHz.340km",
           "system-3.1427-1518MHz.525km", "system-4.1427-2690MHz.690km"],
    "B3": ["system-2.1805-1920MHz.2110-2170MHz.500km", "system-3.2110-2200MHz.340km",
           "system-3.2110-2200MHz.525km", "system-4.1427-2690MHz.690km"],
    "B4": ["system-2.2300-2400MHz.500km", "system-3.2300-2690MHz.340km",
           "system-3.2300-2690MHz.525km", "system-4.1427-2690MHz.690km"],
    "B5": ["system-2.2500-2690MHz.500km", "system-3.2300-2690MHz.340km",
           "system-3.2300-2690MHz.525km", "system-4.1427-2690MHz.690km"],
}

DC_MSS_LOAD_FACTORS = [
    # 0.2,
    0.5,
]

IMT_IDS = [
    "imt.1-3GHz.macrocell.aas-urban-macro-bs",
    "imt.1-3GHz.macrocell.aas-suburban-macro-bs",
    "imt.1-3GHz.macrocell.aas-rural-macro-bs",
]
POWER_BACKOFF_VALUES = [
    # 0., 10., 15.,
    0.,
]

# LINKS = ["dl"]
LINKS = ["ul"]
# LINKS = ["dl"]
# LINKS = ["dl", "ul"]

IMT_MSS_DC_ID_TO_READABLE = {
    "system-2.694MHz.698-960MHz.500km": "Sys2",
    "system-2.1427-1518MHz.500km": "Sys2",
    "system-2.1805-1920MHz.2110-2170MHz.500km": "Sys2",
    "system-2.2300-2400MHz.500km": "Sys2",
    "system-2.2500-2690MHz.500km": "Sys2",
    "system-3.698-960MHz.340km": "Sys3 340km",
    "system-3.698-960MHz.525km": "Sys3 525km",
    "system-3.2110-2200MHz.340km": "Sys3 340km",
    "system-3.2110-2200MHz.525km": "Sys3 525km",
    "system-3.2300-2690MHz.340km": "Sys3 340km",
    "system-3.2300-2690MHz.525km": "Sys3 525km",
    "system-4.698-960MHz.block2.690km": "Sys4 690km",
    "system-4.1427-2690MHz.690km": "Sys4 690km",
}

def get_specific_pattern(
    imt_id: str,
    dc_mss_id: str,
    co_channel: bool,
    band_id: str,
    border: int,
    mss_d2d_load_factor: float,
    link: str,
    pow_backoff: int
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    return f"{dc_mss_id}_{imt_id}_{"co" if co_channel else "adj"}_{band_id}band_{border}km_{mss_d2d_load_factor}load_{link}_{int(pow_backoff)}backoff"

def generate(
    num_snapshots: int,
    co_channel: bool,
    band_id: str,
    choosen_mss_ids: str,
):
    general = {
        "seed": 1026,
        ###########################################################################
        # Number of simulation snapshots
        ###########################################################################
        "num_snapshots": int(num_snapshots),
        "overwrite_output": False,
        "system": "MSS_D2D",
    }

    factory = ParametersFactory()

    for imt_id, dc_mss_id, load_factor, link, pow_backoff  in product(IMT_IDS, choosen_mss_ids, DC_MSS_LOAD_FACTORS, LINKS, POWER_BACKOFF_VALUES):
        imt_freq_mhz = IMT_BAND_CONFIG_MAP[band_id]['imt_dl_center_f_mhz'] if link == "dl" \
            else IMT_BAND_CONFIG_MAP[band_id]['imt_ul_center_f_mhz']
        # if imt_freq_mhz < 1e3:
        #     imt_id = "imt.below-1GHz.single-bs.macro-bs"
        # else:
        #     imt_id = "imt.1-3GHz.single-bs.aas-macro-bs"

        print(f"Generating parameters for IMT {imt_id} and MSS-DC {dc_mss_id} with load factor {load_factor} and link {link}...")
        ####### Power control zones configuration
        # Inject power backoff zone parameters
        mss_params_dict = factory._get_param_as_dict(factory._get_param_dir(dc_mss_id))
        mss_params_dict['mss_d2d']['power_control_zones'] = {}
        mss_params_dict['mss_d2d']['power_control_zones']['zones'] = pwr_ctrl_zone_params['power_control_zones']['zones']
        mss_params_dict['mss_d2d']['power_control_zones']['zones'][1]['power_backoff_db'] = pow_backoff

        params = factory.load_from_id(
            imt_id
        ).load_from_dict(
            mss_params_dict
        ).load_from_dict(
            {"general": general}
        ).build()

        #####
        # scenario
        params.general.imt_link = "DOWNLINK" if link == "dl" else "UPLINK"
        params.imt.interfered_with = True
        params.imt.frequency = imt_freq_mhz
        params.imt.bandwidth = IMT_BAND_CONFIG_MAP[band_id]['typical_bw']
        params.general.enable_cochannel = co_channel
        params.general.enable_adjacent_channel = True  # always on to generate out-of-band emissions
        params.imt.adjacent_ch_reception = "OFF"  # we want only the interference inside IMT rx band

        # Enable intra cell SINR calculation.
        params.imt.imt_dl_intra_sinr_calculation_disabled = False
        # Only the central BS causes interference to the MSS-DC, to avoid simulating a very large number of BSs for the 
        # macrocell scenario. This is also a worst case assumption in terms of interference.
        params.imt.central_bs_interference_only = True

        # Only one cluster considered when computing central cell interference only
        params.imt.topology.macrocell.num_clusters = 1

        # Using FSPL between BS and UE for worst case intra-cell interference.
        params.imt.channel_model = "UMa"

        #######
        # imt parameters
        # International Friendship Bridge
        params.imt.topology.central_latitude = -25.5549751
        params.imt.topology.central_longitude = -54.5746686
        params.imt.topology.central_altitude = 200

        ########### DC-MSS to IMT propagation model
        # # Parameters used for P.619
        # WARNING: Remember to set the lut in propagation/Dataset!
        params.mss_d2d.channel_model = "P619"
        params.mss_d2d.param_p619.earth_station_lat_deg = -25.5549751
        params.mss_d2d.param_p619.earth_station_alt_m = 200

        # Clutter loss parameters vary with IMT deployment
        # We assume mid-rise for all deployments - 8 < hm ≤ 20m
        # UE is always below rooftop, but we're not sure about how that intereacts with indoor model. We shall
        # apply clutter only for outdoor UES and building loss only to indoor UES? Anyway, right now both are
        # considered (they are summed).
        params.mss_d2d.param_p619.mean_clutter_height = "mid"
        if "-urban" in imt_id:
            params.mss_d2d.param_p619.below_rooftop = 50.0 if link == "ul" else 100.0
        else:
            params.mss_d2d.param_p619.below_rooftop = 0.0 if link == "ul" else 100.0

        # Polarization loss - following Item 2.2 of the Rec. ITU-P.619
        params.mss_d2d.polarization_loss = 3.0  # dB

        # Co-channel frequency configuretion - adjacent channel case is set below
        # Overlaps with the left edge of the IMT band.
        params.mss_d2d.bandwidth = DC_MSS_BANDWIDTH_MHZ
        params.mss_d2d.frequency = params.imt.frequency - params.imt.bandwidth / 2 + params.mss_d2d.bandwidth / 2

        ###### Adjust parameters for adjacent channel case
        if not co_channel:
            params.imt.adjacent_ch_reception = "ACS"
            # params.imt.adjacent_ch_reception = "OFF"
            # IMT adjacent channel selectivity - Table 6.5.1-2 - 3GPP TR 38.863
            if link == "ul":
                params.imt.bs.adjacent_ch_selectivity = 46.0  # dB
            else:
                params.imt.ue.adjacent_ch_selectivity = 33.0  # dB
            # Set DC-MSS frequency to the left edge of the IMT band.
            params.mss_d2d.frequency = params.mss_d2d.frequency - params.mss_d2d.bandwidth

        # if "system4" in dc_mss_id:
        #     print("Using Phased Array antenna pattern for System4")
        #     params.mss_d2d.antenna.pattern = "ARRAY System 4"

        # Set system specific adjacent channel emissions parameters
        if "system-3" in dc_mss_id:
            # Adjacent antenna parameters
            # NOTE: Specific to System3 model
            # Accoring to SpaceX the adjacent channel emissions are measured per satellite, not per beam.
            # To cope with SpaceX OOBE model we use a "virtual" antenna for each beam that points to nadir.
            # The gain of this virutal antenna is set in such a way that the summation of all beams is equivalent
            # to a single beam for the whole satellite.
            params.mss_d2d.use_oob_antenna = True
            params.mss_d2d.oob_antenna.pattern = "Antenna System3 OOB"
            params.mss_d2d.oob_antenna.gain = 0.0

            # OOBE mask
            params.mss_d2d.spectral_mask = "STEPPED"
            system3_eirp_mask_vals = \
                np.array([-55.6, -73.6, -83.6]) + 90 + \
                20 * np.log10(params.mss_d2d.frequency / 2000.0)
            system3_eirp_mask_vals = np.concatenate((system3_eirp_mask_vals, [params.mss_d2d.spurious_emissions]))
            params.mss_d2d.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])

        elif "system-4" in dc_mss_id:
            # Adjacente antenna model is the same as in-band.
            params.mss_d2d.use_oob_antenna = False
            params.mss_d2d.adjacent_ch_emissions = "SPECTRAL_MASK"
            params.mss_d2d.spectral_mask = "STEPPED"
            system3_eirp_mask_vals = \
                params.mss_d2d.tx_power_density + 90 - np.array([45, 50])
            system3_eirp_mask_vals = np.concatenate((system3_eirp_mask_vals, [params.mss_d2d.spurious_emissions]))
            params.mss_d2d.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])

        ###### DC-MSS service area and beam pointing
        ########### Sat is active if
        params.mss_d2d.sat_is_active_if.conditions = [
            "LAT_LONG_INSIDE_COUNTRY",
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        params.mss_d2d.sat_is_active_if.lat_long_inside_country.country_names = [
            "Brazil", "Argentina"]
        # params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = \
        #     params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border

        ########## Beam pointing
        params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
        params.mss_d2d.beam_positioning.service_grid.transform_grid_randomly = True
        params.mss_d2d.beam_positioning.service_grid.grid_in_zone.type = "FROM_COUNTRIES"
        params.mss_d2d.beam_positioning.service_grid.grid_in_zone.from_countries.country_names = [
            "Brazil", "Argentina"]
        # This is distance in km so that actual best satellite is used for each grid point
        params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = -200

        print(f"[IMT TN {params.general.imt_link}]:")
        print(f"\tCell radius: ", params.mss_d2d.cell_radius)

        min_margin = round(params.mss_d2d.cell_radius / 1e3, 0)
        # distances = [min_margin, 2 * min_margin]
        distances = [min_margin,]
        print("\tScenarios of grid border as ", distances)

        # Point the IMT-BS to east - worst case scenario
        params.imt.topology.single_bs.azimuth = [0.0]

        params.mss_d2d.beams_load_factor = load_factor
        ds = distances
        for border in ds:
            params.mss_d2d.beam_positioning.service_grid.grid_in_zone.from_countries.margin_from_border = border
            params.general.output_dir = f"{CAMPAIGN_DIR}/output/"
            postfix = get_specific_pattern(
                imt_id,
                dc_mss_id,
                co_channel,
                band_id,
                border,
                load_factor,
                link,
                pow_backoff,
            )
            params.general.output_dir_prefix = f"output_mss_d2d_to_imt_macro_{postfix}"
            file = INPUTS_DIR / f"parameter_mss_d2d_to_imt_macro_{postfix}.yaml"

            # Create parent directories if they don't exist
            dump_parameters(
                file, params
            )

def clear_inputs():
    """Removes all current inputs in inputs directory"""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Clearing inputs from dir '{INPUTS_DIR}'")

    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()


def cmd_line_parser() -> argparse.Namespace:
    """ Parses command line arguments for the campaign. Returns an argparse.Namespace object with the arguments."""
    parser = argparse.ArgumentParser(description="MSS D2D to IMT cross border")

    parser.add_argument(
        "--adj",
        action="store_true",
        help="Whether to use only adjacent channel (true/false). Default: false",
    )
    parser.add_argument(
        "--mss_ids",
        metavar='STRING',
        type=str,
        nargs='+',
        default=DC_MSS_IDS[3],  # "system-3.2110-2200MHz.525km"
        help=f"Space-separated list of mss system IDs to use. Choose from {DC_MSS_IDS}"
    )
    parser.add_argument(
        "--band_id",
        type=str,
        default="B3",
        help=f"Name of IMT band to use. Choose one of {list(IMT_BAND_CONFIG_MAP.keys())}"
    )
    parser.add_argument(
        "--num-of-drops", "-n",
        type=int,
        default=int(1e4),
        help="Number of drops to be simulated"
    )
    parser.add_argument(
        "--dont-clear",
        action="store_true",
        help="Mark true if you wish to NOT remove previous parameter "
        "files in the directory (true/false). Default: false",
    )
    return parser

if __name__ == "__main__":

    args = cmd_line_parser().parse_args()


    if args.band_id != "B3":
        raise ValueError(f"Ooops, sorry we did it only for B3 band for this scenario.")

    for mid in args.mss_ids:
        if mid not in DC_MSS_IDS:
            raise ValueError(f"Invalid MSS ID '{mid}'. Choose from {DC_MSS_IDS}")
        if mid not in BAND_TO_DC_MSS_ID_MAP[args.band_id]:
            raise ValueError(f"MSS ID '{mid}' is not compatible with band {args.band_id}. Choose from {BAND_TO_DC_MSS_ID_MAP[args.band_id]}")

    INPUTS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.dont_clear:
        clear_inputs()

    print(f"Outputting input files to {CAMPAIGN_DIR}")
    print(f"Band designation: {args.band_id}-{IMT_BAND_CONFIG_MAP[args.band_id]['lower']}-{IMT_BAND_CONFIG_MAP[args.band_id]['upper']}MHz")
    print(f"IMT Bandwidth: {IMT_BAND_CONFIG_MAP[args.band_id]['typical_bw']} MHz")
    print(f"IMT frequency: {IMT_BAND_CONFIG_MAP[args.band_id]['imt_dl_center_f_mhz']} MHz (DL), {IMT_BAND_CONFIG_MAP[args.band_id]['imt_ul_center_f_mhz']} MHz (UL)"    )
    print(f"DC-MSS IDs: {args.mss_ids}")
    print(f"Co-channel: {not args.adj}")
    print(f"Number of drops: {args.num_of_drops}")

    generate(
        args.num_of_drops,
        not args.adj,
        args.band_id,
        args.mss_ids,
    )
    n_of_inputs = np.sum([item.name.endswith(".yaml")
                         for item in INPUTS_DIR.iterdir()])
    print("Number of input files: ", n_of_inputs)
