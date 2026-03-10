import numpy as np

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters

from sharc.parameters.antenna.parameters_antenna_s1528 import ParametersAntennaS1528
from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

from campaigns.mss_d2d_to_eess.constants import CAMPAIGN_STR, CAMPAIGN_NAME, get_specific_pattern, INPUTS_DIR

SEED = 0xeffec7  # Example seed value, can be changed as needed
general = {
    "seed": SEED,
    ###########################################################################
    # Number of simulation snapshots
    ###########################################################################
    "num_snapshots": 10000,
    # ,
    # if FALSE, then a new output directory is created,
    "overwrite_output": False,
    # ,
    # output destination folder - this is relative SHARC/sharc directory,
    "output_dir": f"{CAMPAIGN_STR}/output/",
    "output_dir_prefix": "to-update",
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "DOWNLINK",
}


def estimate_eess_antenna_diameter(
    frequency,
    antenna_gain,
    antenna_efficiency
):
    # antenna efficiency:
    n = antenna_efficiency
    lmbda = 3e8 / (frequency * 1e6)
    G = 10**(antenna_gain / 10)
    return float(np.round(
        lmbda * np.sqrt(G / n) / np.pi, decimals=2
    ))


def generate_inputs():
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Inputs going to directory '{INPUTS_DIR}'")

    factory = ParametersFactory()

    for imt_mss_dc_id in [
        "imt.1427-2690MHz.mss-dc.system4-690km",
    ]:
        for eess_sys_id in [
            "eess.2200-2290MHz.system-B",
            "eess.2200-2290MHz.system-D",
        ]:
            print(f"[Building params for {imt_mss_dc_id} -> {eess_sys_id}]")

            params = factory.load_from_id(
                imt_mss_dc_id
            ).load_from_id(
                eess_sys_id
            ).load_from_dict(
                {"general": general}
            ).build()

            ##########
            # Scenario

            params.general.enable_adjacent_channel = True  # this adjacent study only
            params.general.enable_cochannel = False
            params.imt.interfered_with = False
            # NOTE: needed for performance. Discards unnecessary calcs.
            params.imt.imt_dl_intra_sinr_calculation_disabled = True

            ######### Adjacent parameters specific to system4
            # Adjacent antenna model is the same as in-band.
            # params.imt.adjacent_ch_emissions = "ACLR"
            # OOBE mask
            params.imt.spurious_emissions = -30
            params.imt.adjacent_ch_emissions = "SPECTRAL_MASK"
            params.imt.spectral_mask = "STEPPED"
            system3_eirp_mask_vals = \
                params.imt.bs.conducted_power - 10 * np.log10(params.imt.bandwidth) - np.array([45, 50])
            system3_eirp_mask_vals = np.concatenate((system3_eirp_mask_vals, [params.imt.spurious_emissions]))
            params.imt.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])
            params.imt.bs.use_oob_antenna = False

            # channel parameters for EESS station
            params.single_earth_station.frequency = 2200 + \
                params.single_earth_station.bandwidth / 2
            # NOTE: it seems that ACS was not used in previous iterations
            params.single_earth_station.adjacent_ch_reception = "OFF"

            # Geometry
            # Refernce latitude and longitude taken from Cuiaba station
            params.imt.topology.central_latitude = -15.3300
            params.imt.topology.central_longitude = -56.0400
            params.imt.topology.central_altitude = 165

            # position ES at reference
            eess_geom = params.single_earth_station.geometry
            eess_geom.height = 15
            eess_geom.location.type = "FIXED"
            eess_geom.location.fixed.x = 0
            eess_geom.location.fixed.y = 0

            eess_geom.azimuth.type = "UNIFORM_DIST"
            eess_geom.azimuth.uniform_dist.max = 180.
            eess_geom.azimuth.uniform_dist.min = -180.

            eess_geom.elevation.type = "UNIFORM_DIST"
            eess_geom.elevation.uniform_dist.min = 5.
            eess_geom.elevation.uniform_dist.max = 90.

            # 3dB polarization loss, as suggested by P.619
            params.single_earth_station.polarization_loss = 3
            params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
            params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude
            # NOTE: we chose rural/low cluttered environment since MSS UEs are normally there
            params.single_earth_station.param_p619.mean_clutter_height = "low"
            params.single_earth_station.param_p619.below_rooftop = 0.  # zero means clutter loss is not applied

            params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
            params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude

            ##########
            # MSS DC Parameters

            # Beam pointing
            # params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
            # params.imt.topology.mss_dc.beam_positioning.service_grid.country_names = [
            #     "Brazil", "Argentina", "Bolivia", "Chile", "Peru", "Paraguay", "Uruguay"
            # ]
            # # this is distance in km so that actual best satellite is used for each grid point
            # angle_dist_between_planes = 360 / \
            #     params.imt.topology.mss_dc.orbits[0].n_planes
            # margin = -np.ceil((angle_dist_between_planes / 2) * 111)
            # params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = int(
            #     margin)

            # # Beam is active if satellite
            # params.imt.topology.mss_dc.sat_is_active_if.conditions = [
            #     "LAT_LONG_INSIDE_COUNTRY",
            #     "MINIMUM_ELEVATION_FROM_ES",
            # ]
            # params.imt.topology.mss_dc.sat_is_active_if.lat_long_inside_country.country_names = [
            #     "Brazil", "Argentina", "Bolivia", "Chile", "Peru", "Paraguay", "Uruguay"
            # ]
            # params.imt.topology.mss_dc.sat_is_active_if.lat_long_inside_country.margin_from_border = \
            #     params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border

            # Create a circular service grid centered at Cuiabá
            params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
            params.imt.topology.mss_dc.beam_positioning.service_grid.transform_grid_randomly = True
            params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.type = "CIRCLE"
            params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lat = \
                params.imt.topology.central_latitude
            params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lon = \
                params.imt.topology.central_longitude
            params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.radius_km = 1500.0
            params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = 0.0
            # Set a narrower elevation angle to increase the chance to have a server satellite
            params.imt.topology.mss_dc.sat_is_active_if.minimum_elevation_from_es = 23.5  # Degree

            # Create a circular exclusion radius arround the victim station
            grid_exclusion_zone = params.imt.topology.mss_dc.beam_positioning.service_grid.grid_exclusion_zone
            grid_exclusion_zone.type = "CIRCLE"
            grid_exclusion_zone.circle.center_lat = params.imt.topology.central_latitude
            grid_exclusion_zone.circle.center_lon = params.imt.topology.central_longitude
            # Exclusion radius varied in exclusion radius scenario bellow
            # grid_exclusion_zone.circle.radius_km = 0.00001

            params.imt.topology.mss_dc.beam_radius = 24e3
            params.imt.topology.mss_dc.beam_positioning.service_grid.minimum_service_angle = 32.
            print(
                f"A cell radius of {params.imt.topology.mss_dc.beam_radius} will be used for MSS DC")

            ##########
            # EESS Parameters
            if params.single_earth_station.antenna.pattern == "ITU-R S.465":
                antenna_model_param = params.single_earth_station.antenna.itu_r_s_465
            else:
                raise ValueError(
                    f"Script cannot deal with antenna pattern {params.single_earth_station.antenna.pattern}"
                )

            # antenna efficiency
            n = 0.5
            diam = estimate_eess_antenna_diameter(
                params.single_earth_station.frequency,
                params.single_earth_station.antenna.gain,
                n
            )

            print(
                f"\t- An antenna diameter of {diam} "
                f"has been assumed for an efficiency of {n}."
            )
            antenna_model_param.diameter = diam

            params.imt.spurious_emissions = -13
            for excl_radius_km in [
                0.0001,
                1 * params.imt.topology.mss_dc.beam_radius / 1000,
                2 * params.imt.topology.mss_dc.beam_radius / 1000
            ]:
                grid_exclusion_zone.circle.radius_km = excl_radius_km
                for load in [
                    0.2,
                    0.5,
                ]:
                    params.imt.bs.load_probability = load
                    for freq_offset in [
                        0,
                        5,
                    ]:
                        readable_offset = {
                            0: "first_adj",
                            5: "second_adj",
                        }[freq_offset]

                        params.imt.bandwidth = 5  # MHz
                        params.imt.frequency = 2200 - params.imt.bandwidth / 2 - freq_offset

                        specific = get_specific_pattern(
                            "uniform", eess_sys_id, imt_mss_dc_id, readable_offset, excl_radius_km, load
                        )
                        params.general.output_dir_prefix = OUTPUT_START_NAME + specific

                        dump_parameters(
                            INPUTS_DIR / (PARAMETER_START_NAME +
                                        specific + ".yaml"),
                            params,
                        )


def clear_inputs():
    print(f"Clearing inputs from dir '{INPUTS_DIR}'")
    # removes all current inputs in directory
    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()


if __name__ == "__main__":
    clear_inputs()
    generate_inputs()
