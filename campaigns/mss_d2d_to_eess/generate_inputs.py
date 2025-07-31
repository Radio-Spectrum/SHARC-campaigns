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
    ###########################################################################,
    # if FALSE, then a new output directory is created,
    "overwrite_output": False,
    ###########################################################################,
    # output destination folder - this is relative SHARC/sharc directory,
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

    for eess_sys_id in [
        "eess.2200-2290MHz.system-B",
        "eess.2200-2290MHz.system-D",
    ]:
        print(f"[Building params for {eess_sys_id}]")

        params = factory.load_from_id(
            "imt.2110-2200MHz.mss-dc.system3-525km"
        ).load_from_id(
            eess_sys_id
        ).load_from_dict(
            {"general": general}
        ).build()

        ##########
        # Scenario

        params.general.enable_adjacent_channel = True
        params.general.enable_cochannel = False
        params.imt.interfered_with = False
        # NOTE: needed for performance. Discards unnecessary calcs.
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        # NOTE: consider using 2197.5 MHz for directly adjacent simulation
        params.imt.frequency = 2160.0
        params.imt.adjacent_ch_emissions = "SPECTRAL_MASK"

        params.single_earth_station.frequency = 2200 + params.single_earth_station.bandwidth / 2
        # NOTE: it seems that ACS was not used in previous iterations
        params.single_earth_station.adjacent_ch_reception = "ACS"

        # Geometry
        ## Refernce latitude and longitude taken from INPE/Cachoeria Paulista
        params.imt.topology.central_latitude = -22.681603
        params.imt.topology.central_longitude = -45.002609
        params.imt.topology.central_altitude = 563

        # position ES at reference
        eess_geom = params.single_earth_station.geometry
        eess_geom.location.type = "FIXED"
        eess_geom.location.fixed.x = 0
        eess_geom.location.fixed.y = 0

        # Parameters used for P.619
        # WARNING: Remember to set the lut in propagation/Dataset!
        params.single_earth_station.season = "SUMMER"
        # params.single_earth_station.channel_model = "FSPL"
        params.single_earth_station.channel_model = "P619"
        params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
        params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude
        # TODO: decide on these params:
        params.single_earth_station.param_p619.mean_clutter_height = "low"
        params.single_earth_station.param_p619.below_rooftop = 50

        ##########
        # MSS DC Parameters

        # Beam pointing
        params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
        params.imt.topology.mss_dc.beam_positioning.service_grid.country_names = ["Brazil"]
        # this is distance in km so that actual best satellite is used for each grid point
        angle_dist_between_planes = 360 / params.imt.topology.mss_dc.orbits[0].n_planes
        margin = -np.ceil((angle_dist_between_planes / 2) * 111)
        params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = int(margin)

        # Beam is active if satellite
        params.imt.topology.mss_dc.sat_is_active_if.conditions = [
            "LAT_LONG_INSIDE_COUNTRY",
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        params.imt.topology.mss_dc.sat_is_active_if.lat_long_inside_country.country_names = ["Brazil"]
        params.imt.topology.mss_dc.sat_is_active_if.lat_long_inside_country.margin_from_border = \
            params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border

        # Set adjacent antenna pattern
        # NOTE: currently adjacent antenna pattern is
        # M2101 single element
        # this may not be the best modelling
        # TODO: have some way of defining this at parameter level?
        # maybe have some modifier so that we may import `id:adjacent`?
        # or some "parameter level" utility for mounting some
        # kinds of parameter?
        params.imt.bs.antenna.pattern = "ARRAY"

        # Get cell radius based on co-channel antenna pattern
        params.imt.bs.antenna.itu_r_s_1528.frequency = params.imt.frequency
        params.imt.bs.antenna.set_external_parameters(
            frequency=params.imt.frequency,
        )
        # params.imt.validate("propagating-imt")
        params.imt.topology.mss_dc.beam_radius = get_taylor_cell_radius(
            params.imt.bs.antenna.itu_r_s_1528,
            params.imt.topology.mss_dc.orbits[0].apogee_alt_km,
        )

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

        eess_geom.azimuth.type = "UNIFORM_DIST"
        eess_geom.azimuth.uniform_dist.max = 180.
        eess_geom.azimuth.uniform_dist.min = -180.

        for eess_elev in [
            5, 30, 60, 90
        ]:
            params.single_earth_station.geometry.elevation.type = "FIXED"
            params.single_earth_station.geometry.elevation.fixed = eess_elev
            specific = get_specific_pattern(eess_elev, eess_sys_id)
            params.general.output_dir_prefix = OUTPUT_START_NAME + specific

            dump_parameters(
                INPUTS_DIR / (PARAMETER_START_NAME + specific + ".yaml"),
                params,
            )

        # also do uniform dist of elevation angles
        params.single_earth_station.geometry.elevation.type = "UNIFORM_DIST"
        params.single_earth_station.geometry.elevation.uniform_dist.min = 5
        params.single_earth_station.geometry.elevation.uniform_dist.max = 90

        specific = get_specific_pattern("uniform", eess_sys_id)
        params.general.output_dir_prefix = OUTPUT_START_NAME + specific

        dump_parameters(
            INPUTS_DIR / (PARAMETER_START_NAME + specific + ".yaml"),
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
