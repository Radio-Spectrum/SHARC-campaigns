from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

from campaigns.mss_d2d_to_imt_cross_border.cmd_parser import get_cmd_parser

from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

import numpy as np

CAMPAIGN_NAME = "mss_d2d_to_imt_cross_border"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

def get_output_dir_start(mss_id: str, co_channel: bool):
    return f"output_{mss_id}_{"co" if co_channel else "adj"}"

def generate(
    num_snapshots: int,
    mss_id: str,
    co_channel: bool,
):
    print(f"Generating inputs for {mss_id}, co_channel={co_channel}")
    general = {
        "seed": 101,
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

    params.imt.frequency = 2160.0
    params.mss_d2d.frequency = 2160.0

    if not co_channel:
        params.mss_d2d.frequency += (
            params.imt.bandwidth + params.mss_d2d.bandwidth
        ) / 2

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
    params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
    params.mss_d2d.beam_positioning.service_grid.country_names = ["Brazil", "Argentina"]
    # this is distance in km so that actual best satellite is used for each grid point
    angle_dist_between_planes = 360 / params.mss_d2d.orbits[0].n_planes
    margin = -np.ceil((angle_dist_between_planes / 2) * 111)
    params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border = int(margin)

    # Beam is active if
    params.mss_d2d.sat_is_active_if.conditions = [
        "LAT_LONG_INSIDE_COUNTRY",
        "MINIMUM_ELEVATION_FROM_ES",
    ]
    params.mss_d2d.sat_is_active_if.lat_long_inside_country.country_names = ["Brazil", "Argentina"]
    params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = \
        params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border

    # Get cell radius
    params.mss_d2d.antenna_s1528.frequency = params.mss_d2d.frequency
    antenna = AntennaS1528Taylor(
        params.mss_d2d.antenna_s1528
    )
    off_axis = np.linspace(0, 20, int(1e6))
    gains = antenna.calculate_gain(
        off_axis_angle_vec=off_axis,
        theta_vec=0,
    )
    angle_7dB_i = np.where(gains <= params.mss_d2d.antenna_s1528.antenna_gain - 7)[0][0]
    angle_7dB = off_axis[angle_7dB_i]
    cell_radius = np.tan(np.deg2rad(angle_7dB)) * params.mss_d2d.orbits[0].apogee_alt_km * 1e3

    # apprx. 36675.5
    params.mss_d2d.cell_radius = int(cell_radius)
    print("Calculated cell radius: ", params.mss_d2d.cell_radius)

    distances = np.linspace(params.mss_d2d.cell_radius / 1e3, 100, 4)
    distances = [float(round(d, 3)) for d in distances]
    print("Scenarios of grid border as ", distances)
    for load in [0.2, 0.5]:
        params.mss_d2d.beams_load_factor = load

        for link in ["dl", "ul"]:
            params.general.imt_link = "DOWNLINK" if link == "dl" else "UPLINK"

            for border in distances:
                params.mss_d2d.beam_positioning.service_grid.grid_margin_from_border = border
                output_start = get_output_dir_start(mss_id, co_channel)
                params.general.output_dir = f"{CAMPAIGN_STR}/{output_start}_{link}/"

                postfix = f"mss_d2d_to_imt_cross_border_{border}km_{load}load_{link}"
                params.general.output_dir_prefix = f"output_{postfix}"
                file = INPUTS_DIR / f"parameter_{postfix}.yaml"

                # Create parent directories if they don't exist
                dump_parameters(
                    file, params
                )

if __name__ == "__main__":
    parser = get_cmd_parser()
    parser.add_argument(
        "--num-of-drops", "-n",
        type=int,
        default=int(1e5),
        help="Number of drops to be simulated"
    )
    parser.add_argument(
        "--only-generate",
        action="store_true",
        help="Whether to not run campaign, only generate parameters (true/false). Default: false",
    )
    args = parser.parse_args()

    INPUTS_DIR.mkdir(parents=True, exist_ok=True)

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

    if not args.only_generate:
        from sharc.run_multiple_campaigns_mut_thread import run_campaign

        # Run the campaigns
        # This function will execute the campaign with the given name.
        # It will look for the campaign directory under the specified name and
        # start the necessary processes.
        run_campaign(CAMPAIGN_NAME)
