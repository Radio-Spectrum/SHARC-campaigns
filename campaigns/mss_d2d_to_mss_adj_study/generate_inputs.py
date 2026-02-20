from itertools import product
import numpy as np

from sharc.parameters.antenna.parameters_antenna_s1528 import ParametersAntennaS1528
from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.mss_d2d_to_mss_adj_study.constants import (
    CAMPAIGN_NAME, INPUTS_DIR, OUTPUT_DIR,
    IMT_MSS_DC_IDS, MSS_DC_LOAD_FACTORS, SINGLE_ES_MSS_IDS,
    ES_RX_OFFSETS,
    get_specific_pattern
)

SEED = 82

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
    "num_snapshots": 10,
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

        params.general.enable_adjacent_channel = True
        params.general.enable_cochannel = False
        params.imt.interfered_with = False
        # NOTE: needed for performance. Discards unnecessary calcs.
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        # lower bound of closest DL MSS DC band
        params.imt.frequency = 2162.5
        # Note: ES receive frequency will be varied in loop below

        # Victim's adjacent channel reception characteristics
        params.imt.adjacent_ch_emissions = "SPECTRAL_MASK"
        params.imt.spurious_emissions = -13
        # NOTE: Check the ACS values!!
        params.single_earth_station.adjacent_ch_reception = "ACS"
        params.single_earth_station.adjacent_ch_selectivity = 45

        # Geometry
        # Set the simulaltion reference to City of Asunción, Paraguay
        params.imt.topology.central_latitude = -25.2637
        params.imt.topology.central_longitude = -57.5759
        params.imt.topology.central_altitude = 200

        # Channel Model
        params.single_earth_station.channel_model = "P619"

        # P.619 model parameters.
        # 3dB polarization loss, as suggested by P.619
        params.single_earth_station.polarization_loss = 3
        params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
        params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude
        # NOTE: we chose rural/low cluttered environment since MSS UEs are normally there
        params.single_earth_station.param_p619.mean_clutter_height = "low"
        params.single_earth_station.param_p619.below_rooftop = 0.  # zero means clutter loss is not applied

        ########## MSS DC Parameters ##########
        # Adjacent antenna parameters
        # NOTE: Specific to System3 model
        # Accoring to SpaceX the adjacent channel emissions are measured per satellite, not per beam.
        # To cope with SpaceX OOBE model we use a "virtual" antenna for each beam that points to nadir.
        # The gain of this virutal antenna is set in such a way that the summation of all beams is equivalent
        # to a single beam for the whole satellite.
        params.imt.bs.use_oob_antenna = True
        params.imt.bs.oob_antenna.pattern = "Antenna System3 OOB"
        params.imt.bs.oob_antenna.gain = 0.0

        # OOBE mask
        params.imt.spectral_mask = "STEPPED"
        system3_eirp_mask_vals = \
            np.array([-55.6, -73.6, -83.6]) + 90 + \
            20 * np.log10(params.imt.frequency / 2000.0)
        params.imt.spectral_mask_steps = tuple([float(i) for i in system3_eirp_mask_vals])

        if "340km" in imt_id:
            params.imt.topology.mss_dc.max_num_of_beams = 105
        elif "525km" in imt_id:
            params.imt.topology.mss_dc.max_num_of_beams = 90

        ########### SERVICE GRID ###########
        # Create a circular service grid centered at Asunción with 1000 km of radius.
        params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
        params.imt.topology.mss_dc.beam_positioning.service_grid.transform_grid_randomly = True
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.type = "CIRCLE"
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lat = -25.2637
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lon = -57.5759
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.radius_km = 1000.0
        params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = -200.0

        ########### Active Satellite conditions ###########
        # This is used for the circular grid.
        # Service grid eligible_sats_margin_from_border parameter will limit the extension of active satellites.
        params.imt.topology.mss_dc.sat_is_active_if.conditions = [
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        params.imt.topology.mss_dc.sat_is_active_if.minimum_elevation_from_es = 5.  # Degree

        # Set adjacent antenna pattern
        # Get cell radius based on co-channel antenna pattern
        params.imt.bs.antenna.itu_r_s_1528.frequency = 2000.  # MHz. O D/lambda é fixo para essa antena.
        params.imt.bs.antenna.set_external_parameters(
            frequency=2000,
        ) # 2000 MHz. O D/lambda é fixo para essa antena.
        params.imt.topology.mss_dc.beam_radius = get_taylor_cell_radius(
            params.imt.bs.antenna.itu_r_s_1528,
            params.imt.topology.mss_dc.orbits[0].apogee_alt_km,
        )
        print(f"\tA cell radius of {params.imt.topology.mss_dc.beam_radius} will be used for MSS DC")

        #################### MSS Earth Station geometry ##############
        # position ES at reference
        es_geom = params.single_earth_station.geometry
        es_geom.height = 1.5  # meters
        # Let the MSS Earth station be randomly located within the service area.
        es_geom.location.type = "NETWORK"
        # These coordinates are relative to the topology central longitude - Asunción in this case.
        # es_geom.location.uniform_dist.min_dist_to_center = 1e-2  # make it small - close to center
        # es_geom.location.uniform_dist.max_dist_to_center = 1000e3
        es_geom.location.network.min_dist_to_bs = params.imt.topology.mss_dc.beam_radius

        # Vary antenna pointinhg angles uniformly.
        es_geom.azimuth.type = "UNIFORM_DIST"
        es_geom.azimuth.uniform_dist.max = 180.
        es_geom.azimuth.uniform_dist.min = -180.
        es_geom.elevation.type = "UNIFORM_DIST"
        es_geom.elevation.uniform_dist.max = 90.
        es_geom.elevation.uniform_dist.min = 5.

        for mss_dc_load in MSS_DC_LOAD_FACTORS:
            for es_freq, offset_label, _ in ES_RX_OFFSETS:
                params.imt.bs.load_probability = mss_dc_load
                params.single_earth_station.frequency = es_freq
                
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
