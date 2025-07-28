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

    ul_imt_freq = 2160.0
    dl_imt_freq = 1950.0

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
    # distances = [100.000]
    print("Scenarios of grid border as ", distances)
    for load in [0.2, 0.5]:
        params.mss_d2d.beams_load_factor = load

        for link in ["dl", "ul"]:
            params.general.imt_link = "DOWNLINK" if link == "dl" else "UPLINK"
            params.imt.frequency = dl_imt_freq if link == "dl" else ul_imt_freq
            params.mss_d2d.frequency = params.imt.frequency

            if not co_channel:
                params.mss_d2d.frequency += (
                    params.imt.bandwidth + params.mss_d2d.bandwidth
                ) / 2

            for border in distances:
                params.mss_d2d.beam_positioning.service_grid.grid_margin_from_border = border
                output_start = get_output_dir_start(mss_id, co_channel)
                params.general.output_dir = f"{CAMPAIGN_STR}/{output_start}_{link}/"

                postfix = f"mss_d2d_to_imt_cross_border_{border}km_{load}load_{link}"
                params.general.output_dir_prefix = f"output_{postfix}"
                file = INPUTS_DIR / f"parameter_{mss_id}_{"co" if co_channel else "adj"}_{postfix}.yaml"

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
