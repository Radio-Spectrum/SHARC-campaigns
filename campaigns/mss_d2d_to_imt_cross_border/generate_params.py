from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.mss_d2d_to_imt_cross_border.run import CAMPAIGN_STR, CAMPAIGN_DIR, get_output_dir_start, INPUTS_DIR

from campaigns.mss_d2d_to_imt_cross_border.cmd_parser import get_cmd_parser

from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

import numpy as np


def generate(
    num_snapshots: int,
    mss_id: str,
    co_channel: bool,
):
    print(f"Generating inputs for {mss_id}, co_channel={co_channel}")
    general = {
        "seed": 1026,
        ###########################################################################
        # Number of simulation snapshots
        ###########################################################################
        "num_snapshots": num_snapshots,
        "overwrite_output": False,
        "system": "MSS_D2D",
    }

    factory = ParametersFactory()

    params = factory.load_from_id(
        "imt.1-3GHz.single-bs.aas-macro-bs"
    ).load_from_id(
        mss_id
    ).load_from_dict(
        {"general": general}
    ).build()

    #####
    # scenario
    params.imt.interfered_with = True

    ul_imt_freq = 1930.0
    dl_imt_freq = 2120.0

    params.general.enable_cochannel = co_channel
    params.general.enable_adjacent_channel = True

    params.mss_d2d.adjacent_ch_emissions = "SPECTRAL_MASK"
    params.imt.adjacent_ch_reception = "OFF"

    #######
    # imt parameters
    # International Friendship Bridge
    params.imt.topology.central_latitude = -25.5549751
    params.imt.topology.central_longitude = -54.5746686
    params.imt.topology.central_altitude = 200

    #######
    # mss parameters

    # Beam pointing
    # params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
    # params.mss_d2d.beam_positioning.service_grid.country_names = [
    #     "Brazil", "Argentina"]
    # # this is distance in km so that actual best satellite is used for each grid point
    # angle_dist_between_planes = 360 / params.mss_d2d.orbits[0].n_planes
    # margin = -np.ceil((angle_dist_between_planes / 2) * 111)
    # params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border = int(
    #     margin)

    # Beam is active if
    params.mss_d2d.sat_is_active_if.conditions = [
        "LAT_LONG_INSIDE_COUNTRY",
        "MINIMUM_ELEVATION_FROM_ES",
    ]
    params.mss_d2d.sat_is_active_if.lat_long_inside_country.country_names = [
        "Brazil", "Argentina"]
    # params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = \
    #     params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border

    # Parameters used for P.619
    # WARNING: Remember to set the lut in propagation/Dataset!
    params.mss_d2d.channel_model = "P619"
    params.mss_d2d.param_p619.earth_station_lat_deg = -25.5549751
    params.mss_d2d.param_p619.earth_station_alt_m = 200
    params.mss_d2d.param_p619.mean_clutter_height = "low"

    # Polarization loss - following Item 2.2 of the Rec. ITU-P.619
    params.mss_d2d.polarization_loss = 3.0  # dB

    # for link in ["dl", "ul"]:
    for link in ["dl"]:
        params.general.imt_link = "DOWNLINK" if link == "dl" else "UPLINK"
        params.imt.frequency = dl_imt_freq if link == "dl" else ul_imt_freq
        # Brings DC-MSS to 2110-2120 DL or 1920-1930 ULband
        params.mss_d2d.frequency = params.imt.frequency - 7.5
        ###### Adjust parameters for adjacent channel case
        if not co_channel:
            params.imt.adjacent_ch_reception = "ACS"
            # IMT adjacent channel selectivity - Table 6.5.1-2 - 3GPP TR 38.863
            if link == "ul":
                params.imt.bs.adjacent_ch_selectivity = 46.0  # dB
            else:
                params.imt.ue.adjacent_ch_selectivity = 33.0  # dB
            # Set IMT frequency to be adjacent to DC-MSS
            params.imt.frequency = params.imt.frequency + params.mss_d2d.bandwidth

        # Turn-on adjacent antenna model for both co-channel and adjacent channel studies.
        params.mss_d2d.use_oob_antenna = True

        # Setup adjacent channel emissions
        # In-band antenna
        params.mss_d2d.antenna_pattern = "ITU-R-S.1528-Taylor"
        params.mss_d2d.antenna.pattern = "ITU-R-S.1528-Taylor"
        params.mss_d2d.antenna.gain = 34.1

        # Adjacent antenna parameters
        # NOTE: Specific to System3 model
        # Accoring to SpaceX the adjacent channel emissions are measured per satellite, not per beam.
        # To cope with SpaceX OOBE model we use a "virtual" antenna for each beam that points to nadir.
        # The gain of this virutal antenna is set in such a way that the summation of all beams is equivalent
        # to a single beam for the whole satellite.
        params.mss_d2d.use_oob_antenna = True
        params.mss_d2d.oob_antenna.pattern = "Cosine Antenna"
        params.mss_d2d.oob_antenna.gain = 0.0

        # OOBE mask
        params.mss_d2d.spectral_mask = "STEPPED"
        system3_eirp_mask_vals = \
            np.array([-55.6, -73.6, -83.6]) + 90 + \
            20 * np.log10(params.mss_d2d.frequency / 2000.0)
        params.mss_d2d.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])

        # Here we use the default antenna pattern and gain from the system file
        params.mss_d2d.antenna_pattern = "ITU-R-S.1528-Taylor"
        params.mss_d2d.antenna.pattern = "ITU-R-S.1528-Taylor"
        params.mss_d2d.antenna.gain = 34.1

        # Beam pointing
        params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
        # add per drop rand rotation + transl. to grid
        params.mss_d2d.beam_positioning.service_grid.transform_grid_randomly = True
        params.mss_d2d.beam_positioning.service_grid.grid_in_zone.type = "FROM_COUNTRIES"
        params.mss_d2d.beam_positioning.service_grid.grid_in_zone.from_countries.country_names = [
            "Brazil", "Argentina"]
        # this is distance in km so that actual best satellite is used for each grid point
        angle_dist_between_planes = 360 / params.mss_d2d.orbits[0].n_planes
        margin = -np.ceil((angle_dist_between_planes / 2) * 111)
        params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border = int(
            margin)
        params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = int(margin)

        params.mss_d2d.param_p619.below_rooftop = 0.0 if link == "dl" else 50.0

        # Get cell radius
        # params.mss_d2d.antenna_s1528.frequency = params.mss_d2d.frequency
        params.mss_d2d.antenna.itu_r_s_1528.frequency = 2000.0  # fix lambda=0.15m
        # NOTE: max frequency yields smaller cell radius
        # params.mss_d2d.antenna_s1528.frequency = max(ul_imt_freq, dl_imt_freq)
        antenna = AntennaS1528Taylor(
            params.mss_d2d.antenna.itu_r_s_1528
        )
        off_axis = np.linspace(0, 20, int(1e6))
        gains = antenna.calculate_gain(
            off_axis_angle_vec=off_axis,
            theta_vec=0,
        )
        angle_7dB_i = np.where(
            gains <= 34.1 - 7)[0][0]
        angle_7dB = off_axis[angle_7dB_i]
        cell_radius = np.tan(np.deg2rad(angle_7dB)) * \
            params.mss_d2d.orbits[0].apogee_alt_km * 1e3

        # apprx. 36675.5
        params.mss_d2d.cell_radius = int(cell_radius)
        print(f"[IMT TN {params.general.imt_link}]:")
        print(f"\tCalculated cell radius: ", params.mss_d2d.cell_radius)

        min_margin = round(params.mss_d2d.cell_radius / 1e3, 0)
        distances = [min_margin, 2 * min_margin]
        print("\tScenarios of grid border as ", distances)

        # Point the IMT-BS to east - worst case scenario
        params.imt.topology.single_bs.azimuth = [0.0]

        for load in [0.1, 0.2, 0.5]:
            params.mss_d2d.beams_load_factor = load
            for border in distances:
                params.mss_d2d.beam_positioning.service_grid.grid_in_zone.from_countries.margin_from_border = border

                output_start = get_output_dir_start(mss_id, co_channel)
                params.general.output_dir = f"{CAMPAIGN_STR}/{output_start}_{link}/"

                postfix = f"mss_d2d_to_imt_cross_border_{border}km_{load}load_{link}"
                params.general.output_dir_prefix = f"output_{postfix}"
                file = INPUTS_DIR / \
                    f"parameter_{mss_id}_{"co" if co_channel else "adj"}_{postfix}.yaml"

                # Create parent directories if they don't exist
                dump_parameters(
                    file, params
                )


if __name__ == "__main__":
    parser = get_cmd_parser()
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
    args = parser.parse_args()

    INPUTS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.dont_clear:
        # removes all current inputs in directory
        for item in INPUTS_DIR.iterdir():
            if item.is_file() and item.name.endswith(".yaml"):
                item.unlink()

    print(f"Outputting input files to {CAMPAIGN_DIR}")

    for selected_sys in args.mss:
        generate(
            args.num_of_drops,
            selected_sys,
            not args.adj,
        )
    n_of_inputs = np.sum([item.name.endswith(".yaml")
                         for item in INPUTS_DIR.iterdir()])
    print("Number of input files: ", n_of_inputs)
