from itertools import product
import numpy as np

from sharc.parameters.antenna.parameters_antenna_s1528 import ParametersAntennaS1528
from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.mss_d2d_to_arns_dme_study.constants import (
    CAMPAIGN_NAME, INPUTS_DIR, OUTPUT_DIR, OFFSET_LABELS,
    IMT_MSS_DC_IDS, MSS_DC_LOAD_FACTORS, SINGLE_ES_MSS_IDS,
    get_specific_pattern
)

SEED = 82

MSS_DC_CENTER_FREQ = 970.5  # Mhz
# wp4c 107
# R23 wp4c 528

MSS_DC_TX_OFFSETS = [
    (MSS_DC_CENTER_FREQ, "offset_0MHz", "First adjcent"),
    #(MSS_DC_CENTER_FREQ + 5, "offset_5MHz", "Second adjacent"),
    #(MSS_DC_CENTER_FREQ + 10, "offset_10MHz", "Third adjacent"),
    #(MSS_DC_CENTER_FREQ + , "offset_120MHz", "Spurious domain"),
]

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

general = {
    "seed": SEED,
    "num_snapshots": int(1e4),
    "overwrite_output": False,
    "output_dir": str(OUTPUT_DIR),
    "output_dir_prefix": "to-update",
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "DOWNLINK",
}

def generate_inputs():
    """Generates all campaign input files"""
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Generating input parameters at:\n\t{INPUTS_DIR}")
    factory = ParametersFactory()
    total = 0

    for imt_id, single_es_id in product(IMT_MSS_DC_IDS, SINGLE_ES_MSS_IDS):
        print(f"[Building params for {imt_id} -> {single_es_id}]")

        params = factory.load_from_id(
            imt_id
        ).load_from_id(
            single_es_id
        ).load_from_dict(
            {"general": general}
        ).build()

        ##########
        # Scenario
        # Co-channel by default
        params.general.enable_adjacent_channel = False # We will set it to True for adjacent channel scenarios in loop below
        params.general.enable_cochannel = True # We will set it to False for adjacent channel scenarios in loop below
        params.imt.interfered_with = False
        # NOTE: needed for performance. Discards unnecessary calcs.
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        # NOTE: Check the ACS values!!
        params.single_earth_station.adjacent_ch_reception = "OFF"
        params.single_earth_station.adjacent_ch_selectivity = 45

        # Geometry
        # Set the simulation reference to City of Asunción, Paraguay
        params.imt.topology.central_latitude = -25.2637
        params.imt.topology.central_longitude = -57.5759
        params.imt.topology.central_altitude = 200

        # Channel Model
        params.single_earth_station.channel_model = "FSPL"

        # P.619 model parameters.
        # 3dB polarization loss, as suggested by P.619
        params.single_earth_station.polarization_loss = 3
        params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
        params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude
        # NOTE: we chose rural/low cluttered environment since MSS UEs are normally there
        params.single_earth_station.param_p619.mean_clutter_height = "low"
        params.single_earth_station.param_p619.below_rooftop = 0.  # zero means clutter loss is not applied

        ########## MSS DC Parameters ##########
        # System spefic parameters - NOTE: we should move this to the yaml files for each system
        if "system3" in imt_id:
            params.imt.topology.mss_dc.beam_positioning.service_grid.minimum_service_angle = 20.
            if "340km" in imt_id:
                params.imt.topology.mss_dc.max_num_of_beams = 90
            elif "525km" in imt_id:
                params.imt.topology.mss_dc.max_num_of_beams = 105
        elif "system4" in imt_id:
            params.imt.topology.mss_dc.beam_radius = 24e3
            params.imt.topology.mss_dc.beam_positioning.service_grid.minimum_service_angle = 32.

        ########### SERVICE GRID ###########
        # Create a circular service grid centered at Asunción with 1000 km of radius.
        params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
        params.imt.topology.mss_dc.beam_positioning.service_grid.transform_grid_randomly = True
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.type = "CIRCLE"
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lat = -25.2637
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lon = -57.5759
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.radius_km = 1500.0
        params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = 0.0

        ########### Active Satellite conditions ###########
        # This is used for the circular grid.
        # Service grid eligible_sats_margin_from_border parameter will limit the extension of active satellites.
        params.imt.topology.mss_dc.sat_is_active_if.conditions = [
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        # Aprox. 1000km arround the Earth Station
        params.imt.topology.mss_dc.sat_is_active_if.minimum_elevation_from_es = 23.5  # Degree

        # Get cell radius based on co-channel antenna pattern
        # NOTE: This is specific to system3
        if "system3" in imt_id:
            params.imt.bs.antenna.itu_r_s_1528.frequency = 2000.  # MHz. O D/lambda é fixo para essa antena.
            params.imt.bs.antenna.set_external_parameters(
                frequency=2000,
            )  # 2000 MHz. O D/lambda é fixo para essa antena.
            params.imt.topology.mss_dc.beam_radius = get_taylor_cell_radius(
                params.imt.bs.antenna.itu_r_s_1528,
                params.imt.topology.mss_dc.orbits[0].apogee_alt_km,
            )

        print(f"\tA cell radius of {params.imt.topology.mss_dc.beam_radius} will be used for MSS DC")
        params.imt.bs.use_oob_antenna = False  # will be set to True for adjacent channel scenarios in loop below

        #################### MSS Earth Station Parameters ##############
        # MHz. Setting to the center of the victim ES band (Hibleo-X) to be more conservative.
        params.single_earth_station.frequency = 962 + params.single_earth_station.bandwidth / 2
        # position ES at reference
        es_geom = params.single_earth_station.geometry
        es_geom.height = 10000  # meters
        # Let the MSS Earth station be randomly located within the service area.
        es_geom.location.type = "UNIFORM_DIST"
        # These coordinates are relative to the topology central longitude - Asunción in this case.
        es_geom.location.uniform_dist.min_dist_to_center = 1e-2  # make it small - close to center
        es_geom.location.uniform_dist.max_dist_to_center = 1000e3
    
        0
        # Vary antenna pointinhg angles uniformly.
        es_geom.azimuth.type = "UNIFORM_DIST"
        es_geom.azimuth.uniform_dist.max = 180.
        es_geom.azimuth.uniform_dist.min = -180.
        es_geom.elevation.type = "UNIFORM_DIST"
        es_geom.elevation.uniform_dist.max = 90.
        es_geom.elevation.uniform_dist.min = 5.

        for mss_dc_load in MSS_DC_LOAD_FACTORS:
            for mss_dc_freq, offset_label, _ in MSS_DC_TX_OFFSETS:
                params.imt.frequency = mss_dc_freq
                params.imt.bs.load_probability = mss_dc_load

                is_zero_offset = np.isclose(params.single_earth_station.frequency, params.imt.frequency)

                if not is_zero_offset:  # Adjacent channel scenario

                    params.general.enable_adjacent_channel = True
                    params.general.enable_cochannel = False
                    # Adjacent antenna parameters
                    if "system3" in imt_id:
                        # NOTE: Specific to System3 model
                        # Accoring to SpaceX the adjacent channel emissions are measured per satellite, not per beam.
                        # To cope with SpaceX OOBE model we use a "virtual" antenna for each beam that points to nadir.
                        # The gain of this virutal antenna is set in such a way that the summation of all beams is equivalent
                        # to a single beam for the whole satellite.
                        params.imt.bs.use_oob_antenna = True
                        params.imt.bs.oob_antenna.pattern = "Antenna System3 OOB"
                        params.imt.bs.oob_antenna.gain = 0.0

                        # OOBE mask
                        params.imt.spurious_emissions = -13
                        params.imt.adjacent_ch_emissions = "SPECTRAL_MASK"
                        params.imt.spectral_mask = "STEPPED"
                        system3_eirp_mask_vals = \
                            np.array([-55.6, -73.6, -83.6]) + 90 + \
                            20 * np.log10(params.imt.frequency / 2000.0)
                        system3_eirp_mask_vals = np.concatenate((system3_eirp_mask_vals, [params.imt.spurious_emissions]))
                        params.imt.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])
                    elif "system4" in imt_id:
                        # Adjacente antenna model is the same as in-band.
                        # params.imt.adjacent_ch_emissions = "ACLR"
                        # OOBE mask
                        params.imt.adjacent_ch_emissions = "SPECTRAL_MASK"
                        params.imt.spectral_mask = "STEPPED"
                        system3_eirp_mask_vals = \
                            params.imt.bs.conducted_power - 10 * np.log10(params.imt.bandwidth) - np.array([45, 50])
                        params.imt.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])
                        params.imt.bs.use_oob_antenna = False

                specific = get_specific_pattern(
                    imt_id, single_es_id, mss_dc_load, offset_label
                )
                params.general.output_dir_prefix = OUTPUT_START_NAME + specific

                total += 1
                dump_parameters(
                    INPUTS_DIR / (PARAMETER_START_NAME + specific + ".yaml"),
                    params,
                )

    print(f"\nFiles generated on this run: {total}\n")
    if INPUTS_DIR.exists():
        n_of_inputs = np.sum([item.name.endswith(".yaml") for item in INPUTS_DIR.iterdir()])
        print("Total number of input files: ", n_of_inputs)

def clear_inputs():
    """Removes all current inputs in inputs directory"""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Clearing inputs from dir '{INPUTS_DIR}'")

    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()

if __name__ == "__main__":
    #test_calculate_equivalent_acs()
    clear_inputs()
    generate_inputs()

# diagrama de radiacao da ant
# figura de ruido e temperatura de ruido
# path loss = FSPL
