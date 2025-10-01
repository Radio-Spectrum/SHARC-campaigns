from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.mss_d2d_to_imt_separation_distance.run import CAMPAIGN_STR, CAMPAIGN_DIR, get_output_dir_start, INPUTS_DIR

from sharc.parameters.constants import EARTH_RADIUS

from campaigns.mss_d2d_to_imt_cross_border.cmd_parser import get_cmd_parser, OPTION_TO_SELECTED_IMT_DEPLOYMENT

from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

import numpy as np
import re


EARTH_RADIUS_KM = EARTH_RADIUS / 1e3


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

    for imt_deployment_id in OPTION_TO_SELECTED_IMT_DEPLOYMENT[args.imt_deployment]:
        print(f"Using IMT deployment: {imt_deployment_id}")
        # Extract "urban", "suburban", or "rural" from the IMT deployment ID
        match = re.search(r'\b(urban|suburban|rural)\b', imt_deployment_id)
        imt_deployment_name = match.group(1) if match else None
        print(f"IMT deployment name: {imt_deployment_name}")


        params = factory.load_from_id(
            imt_deployment_id
        ).load_from_id(
            mss_id
        ).load_from_dict(
            {"general": general}
        ).build()

        #####
        # scenario
        params.imt.interfered_with = True

        params.general.enable_cochannel = co_channel
        params.general.enable_adjacent_channel = True

        params.mss_d2d.adjacent_ch_emissions = "SPECTRAL_MASK"
        params.imt.adjacent_ch_reception = "OFF"

        #######
        # imt parameters
        # Positioned at Brasília
        params.imt.topology.central_latitude = -15.793889
        params.imt.topology.central_longitude = -47.882778
        params.imt.topology.central_altitude = 1200

        # These parameters are allinged with Rabie/Biljana
        # IMT parameterrs
        params.imt.frequency = 2300  # MHz
        params.imt.bandwidth = 20  # MHz
        params.imt.guard_band_ratio = 0.0
        params.imt.noise_temperature = 290  # K
        params.imt.bs.antenna.array.minimum_array_gain = -60  # dBi
        params.imt.ue.k = 1  # single UE per cell
        params.imt.uedistribution_distance: "SQRT(UNIFORM)"
        # DC-MSS parameters
        # beam positioning - single beam pointing nadir
        params.mss_d2d.polarization_loss = 0.0  # dB
        params.mss_d2d.num_sectors = 1  # number of beams per satellite
        params.mss_d2d.cell_radius = 39475.0
        params.mss_d2d.beams_load_factor = 1.0  # all beams active
        params.mss_d2d.beam_positioning.type = "ANGLE_FROM_SUBSATELLITE"
        params.mss_d2d.beam_positioning.angle_from_subsatellite_theta.type = "FIXED"
        params.mss_d2d.beam_positioning.angle_from_subsatellite_theta.fixed = 0.0
        params.mss_d2d.beam_positioning.angle_from_subsatellite_phi.type = "FIXED"
        params.mss_d2d.beam_positioning.angle_from_subsatellite_phi.fixed = 0.0

        #######
        # mss parameters

        # Beam pointing
        # Uncomment to use SERVICE_GRID
        # params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
        # params.mss_d2d.beam_positioning.service_grid.country_names = [
        #     "Brazil", "Argentina"]
        # # this is distance in km so that actual best satellite is used for each grid point
        # angle_dist_between_planes = 360 / params.mss_d2d.orbits[0].n_planes
        # margin = -np.ceil((angle_dist_between_planes / 2) * 111)
        # params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border = int(
        #     margin)

        # # Beam is active if
        # params.mss_d2d.sat_is_active_if.conditions = [
        #     "LAT_LONG_INSIDE_COUNTRY",
        #     "MINIMUM_ELEVATION_FROM_ES",
        # ]
        # params.mss_d2d.sat_is_active_if.lat_long_inside_country.country_names = [
        #     "Brazil", "Argentina"]
        # params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = \
        #     params.mss_d2d.beam_positioning.service_grid.eligible_sats_margin_from_border

        sat_alt_km = params.mss_d2d.orbits[0].apogee_alt_km

        # The MAXIMUM_ELEVATION_FROM_ES will be set later according to the exclusion distance
        params.mss_d2d.sat_is_active_if.conditions = []
        params.mss_d2d.sat_is_active_if.conditions.append(
            "MINIMUM_ELEVATION_FROM_ES")
        params.mss_d2d.sat_is_active_if.conditions.append(
            "MAXIMUM_ELEVATION_FROM_ES")
        params.mss_d2d.sat_is_active_if.minimum_elevation_from_es = 5.0

        # Parameters used for P.619
        # WARNING: Remember to set the lut in propagation/Dataset!
        # params.mss_d2d.channel_model = "P619"
        # params.mss_d2d.param_p619.earth_station_lat_deg = -25.5549751
        # params.mss_d2d.param_p619.earth_station_alt_m = 200
        # params.mss_d2d.param_p619.mean_clutter_height = "low"

        params.mss_d2d.channel_model = "FSPL"

        # Polarization loss - following Item 2.2 of the Rec. ITU-P.61
        params.mss_d2d.polarization_loss = 3.0  # dB

        for link in ["dl", "ul"]:
            params.general.imt_link = "DOWNLINK" if link == "dl" else "UPLINK"
            print(f"Link: {link.upper()}")
            if co_channel:
                params.mss_d2d.frequency = params.imt.frequency
            else:
                params.imt.adjacent_ch_reception = "ACS"
                # IMT adjacent channel selectivity - Table 6.5.1-2 - 3GPP TR 38.863
                if link == "ul":
                    params.imt.bs.adjacent_ch_selectivity = 46.0  # dB
                else:
                    params.imt.ue.adjacent_ch_selectivity = 33.0  # dB
                # Set MSS D2D frequency to be adjacent to IMT
                params.mss_d2d.frequency = params.imt.frequency + \
                    params.imt.bandwidth / 2 + params.mss_d2d.bandwidth / 2

            # Some link specific parameters
            params.mss_d2d.param_p619.below_rooftop = 0.0 if link == "dl" else 50.0

            params.mss_d2d.antenna.itu_r_s_1528.frequency = params.mss_d2d.frequency
            # Uncomment to use the calculated cell radius
            # # Get cell radius from 7dB beamwidth
            # # NOTE: max frequency yields smaller cell radius
            # # params.mss_d2d.antenna.itu_r_s_1528.frequency = max(ul_imt_freq, dl_imt_freq)
            # antenna = AntennaS1528Taylor(
            #     params.mss_d2d.antenna.itu_r_s_1528
            # )
            # off_axis = np.linspace(0, 20, int(1e6))
            # gains = antenna.calculate_gain(
            #     off_axis_angle_vec=off_axis,
            #     theta_vec=0,
            # )
            # angle_7dB_i = np.where(
            #     gains <= params.mss_d2d.antenna.itu_r_s_1528.antenna_gain - 7)[0][0]
            # angle_7dB = off_axis[angle_7dB_i]
            # cell_radius = np.tan(np.deg2rad(angle_7dB)) * \
            #     params.mss_d2d.orbits[0].apogee_alt_km * 1e3
            # params.mss_d2d.cell_radius = int(cell_radius)
            print("\tDC-MSS spot-beam radius [km]: ", params.mss_d2d.cell_radius)
            print("\tIMT cell radius [m]: ", params.imt.topology.single_bs.cell_radius)

            # distances = np.linspace(params.mss_d2d.cell_radius / 1e3, 100, 4)
            # distances = [float(round(d, 3)) for d in distances]
            # # distances = [100.000]
            # print("\tScenarios of grid border as ", distances)

            # Separation distances to be tested - this is the separation between the IMT and MSS D2D cell edges
            for separation_dist_km in [np.ceil(-params.mss_d2d.cell_radius / 1e3),
                                       -params.imt.topology.single_bs.cell_radius / 1e3, 0, 1, 5, 10, 20, 50, 100]:

                # Define the exclusion radius around the BS
                exclusion_radius_km = separation_dist_km + params.mss_d2d.cell_radius / 1e3 + \
                    params.imt.topology.single_bs.cell_radius / 1e3  # cell radius is in meters

                # Update the parameters with the new exclusion angle calculated from the exclusion distance
                # The distance is assumed be the arc distance on the surface of the Earth
                central_angle_rad = exclusion_radius_km / EARTH_RADIUS_KM

                # Use cosine law to calculate the slant range
                slant_range = np.sqrt(EARTH_RADIUS_KM**2 + (EARTH_RADIUS_KM + sat_alt_km)**2 -
                                      2 * EARTH_RADIUS_KM * (EARTH_RADIUS_KM + sat_alt_km) * np.cos(central_angle_rad))

                # Calculate the exclusion angle
                alfa_rad = np.arcsin(
                    ((EARTH_RADIUS_KM + sat_alt_km) / slant_range) * np.sin(central_angle_rad))
                exclusion_angle_deg = 90 - np.degrees(alfa_rad)

                if exclusion_radius_km == 0:
                    # If the exclusion distance is 0 km, we set the maximum elevation to 90 degrees
                    params.mss_d2d.sat_is_active_if.maximum_elevation_from_es = 89.99999
                else:
                    params.mss_d2d.sat_is_active_if.maximum_elevation_from_es = float(
                        exclusion_angle_deg)

                print(
                    f'\tExclusion angle for separation distance {separation_dist_km:.1f} km: {exclusion_angle_deg:.2f} degrees')

                # output_start = get_output_dir_start(mss_id, co_channel)
                # params.general.output_dir = f"{CAMPAIGN_STR}/{output_start}_{link}/"
                params.general.output_dir = f"{CAMPAIGN_STR}/output/"

                if separation_dist_km < 0:
                    print(
                        f"\tWarning: Negative separation distance {separation_dist_km} km. This means IMT cell is overlapping MSS D2D cell.")
                    postfix = f"mss_d2d_to_imt_separation_distance_{separation_dist_km}km_{imt_deployment_name}_{link}".replace("-", "neg")
                else:
                    postfix = f"mss_d2d_to_imt_separation_distance_{separation_dist_km}km_{imt_deployment_name}_{link}"
                params.general.output_dir_prefix = f"output_{postfix}"
                file = INPUTS_DIR / \
                    f"parameter_{mss_id}_{"co" if co_channel else "adj"}_{postfix}.yaml"

                print(f"\tSaving parameters to file: {file}")

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

    print(f"Outputting parameter files to {CAMPAIGN_DIR}")

    for selected_sys in args.mss:
        generate(
            args.num_of_drops,
            selected_sys,
            not args.adj,
        )
    n_of_inputs = np.sum([item.name.endswith(".yaml")
                         for item in INPUTS_DIR.iterdir()])
    print("Number of input files: ", n_of_inputs)
