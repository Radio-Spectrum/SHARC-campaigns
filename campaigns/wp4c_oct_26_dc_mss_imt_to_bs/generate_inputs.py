from itertools import product
import numpy as np

from sharc.parameters.antenna.parameters_antenna_s1528 import ParametersAntennaS1528
from sharc.antenna.antenna_s1528 import AntennaS1528Taylor

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.wp4c_oct_26_dc_mss_imt_to_bs.constants import (
    CAMPAIGN_NAME,
    INPUTS_DIR,
    OUTPUT_DIR,
    IMT_MSS_DC_IDS,
    MSS_DC_LOAD_FACTORS,
    BS_IDS,
    BS_CHANNELS,
    BS_REPECTION_TYPE,
    get_specific_pattern
)

SEED = 82

DC_MSS_IMT_DL_BANDWIDTH_MHZ = 5.0  # MHz - DC-MSS-IMT DL bandwidth
IMT_A5_BAND_CENTER_FREQ_MHZ = 758.0 + DC_MSS_IMT_DL_BANDWIDTH_MHZ / 2.0  # MHz - center frequency of A5 band (IMT DL)


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

    for imt_id, bs_id, bs_reception_type in product(IMT_MSS_DC_IDS, BS_IDS, BS_REPECTION_TYPE):
        print(f"[Building params for {imt_id} -> {bs_id}]")

        params = factory.load_from_id(
            imt_id
        ).load_from_id(
            bs_id
        ).load_from_dict(
            {"general": general}
        ).build()

        ##########
        # Scenario
        params.imt.interfered_with = False

        # We fix the DC-MSS-IMT DL transmission at the edge of A5 band for all scenarios
        # so that the BS is either co-channel or adjacent channel.
        params.imt.frequency = IMT_A5_BAND_CENTER_FREQ_MHZ
        # NOTE: needed for performance. Discards unnecessary calcs.
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        # NOTE: Check the ACS values!!
        params.single_earth_station.adjacent_ch_reception = "OFF"
        params.single_earth_station.adjacent_ch_selectivity = 45.  # ignored if adjacent_ch_reception is OFF

        # Geometry
        # Set the simulation reference to City of Letícia, Colombia.
        params.imt.topology.central_latitude = -4.21601
        params.imt.topology.central_longitude = -69.93641
        params.imt.topology.central_altitude = 96.

        # Channel Model
        params.single_earth_station.channel_model = "P619"
        # params.single_earth_station.channel_model = "FSPL"

        # P.619 model parameters.
        # 3dB polarization loss, as suggested by P.619
        params.single_earth_station.polarization_loss = 3
        params.single_earth_station.param_p619.earth_station_lat_deg = params.imt.topology.central_latitude
        params.single_earth_station.param_p619.earth_station_alt_m = params.imt.topology.central_altitude
        # NOTE: we chose rural/low cluttered environment since MSS UEs are normally there
        params.single_earth_station.param_p619.mean_clutter_height = "low"
        params.single_earth_station.param_p619.below_rooftop = 0.  # zero means clutter loss is not applied

        # ########## MSS DC Parameters ##########
        # # System spefic parameters - NOTE: we should move this to the yaml files for each system
        # if "system3" in imt_id:
        #     params.imt.topology.mss_dc.beam_positioning.service_grid.minimum_service_angle = 20.
        #     if "340km" in imt_id:
        #         params.imt.topology.mss_dc.max_num_of_beams = 90
        #     elif "525km" in imt_id:
        #         params.imt.topology.mss_dc.max_num_of_beams = 105
        # elif "system4" in imt_id:
        #     params.imt.topology.mss_dc.beam_radius = 24e3
        #     params.imt.topology.mss_dc.beam_positioning.service_grid.minimum_service_angle = 32.

        ########### SERVICE GRID ###########
        # Create a circular service grid centered at Asunción with 1000 km of radius.
        params.imt.topology.mss_dc.beam_positioning.type = "SERVICE_GRID"
        params.imt.topology.mss_dc.beam_positioning.service_grid.transform_grid_randomly = True
        # params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.type = "CIRCLE"
        # params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lat = -25.2637
        # params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.center_lon = -57.5759
        # params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.circle.radius_km = 1500.0
        # params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = 0.0

        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.type = "FROM_COUNTRIES"
        params.imt.topology.mss_dc.beam_positioning.service_grid.grid_in_zone.from_countries.country_names = [
            "Brazil",
        ]
        # this is distance in km so that actual best satellite is used for each grid point
        # angle_dist_between_planes = 360 / \
        #     params.imt.topology.mss_dc.orbits[0].n_planes
        # margin = -np.ceil((angle_dist_between_planes / 2) * 111)
        # params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = int(
        #     margin)
        params.imt.topology.mss_dc.beam_positioning.service_grid.eligible_sats_margin_from_border = -700

        ########### Active Satellite conditions ###########
        # This is used for the circular grid.
        # Service grid eligible_sats_margin_from_border parameter will limit the extension of active satellites.
        params.imt.topology.mss_dc.sat_is_active_if.conditions = [
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        # Aprox. 1000km arround the Earth Station
        params.imt.topology.mss_dc.sat_is_active_if.minimum_elevation_from_es = 5.  # Degree

        # Get cell radius based on co-channel antenna pattern
        # NOTE: This is specific to system3
        # if "system3" in imt_id:
        #     params.imt.bs.antenna.itu_r_s_1528.frequency = 2000.  # MHz. O D/lambda é fixo para essa antena.
        #     params.imt.bs.antenna.set_external_parameters(
        #         frequency=2000,
        #     )  # 2000 MHz. O D/lambda é fixo para essa antena.

        print(f"\tA cell radius of {params.imt.topology.mss_dc.beam_radius} will be used for MSS DC")
        params.imt.bs.use_oob_antenna = False  # will be set to True for adjacent channel scenarios in loop below

        #################### BS Earth Station Parameters ##############
        # position ES at reference
        es_geom = params.single_earth_station.geometry
        es_geom.height = 1.5  # meters
        # Let the BS Earth station be randomly located within the service area.
        # es_geom.location.type = "NETWORK"
        # These coordinates are relative to the topology central longitude - Asunción in this case.
        # es_geom.location.uniform_dist.min_dist_to_center = 1e-2  # make it small - close to center
        # es_geom.location.uniform_dist.max_dist_to_center = 1000e3
        # es_geom.location.network.min_dist_to_bs = params.imt.topology.mss_dc.beam_radius

        # Vary antenna pointinhg angles uniformly.
        # es_geom.azimuth.type = "UNIFORM_DIST"
        # es_geom.azimuth.uniform_dist.max = 180.
        # es_geom.azimuth.uniform_dist.min = -180.
        # es_geom.elevation.type = "UNIFORM_DIST"
        # es_geom.elevation.uniform_dist.max = 90.
        # es_geom.elevation.uniform_dist.min = 5.

        if bs_reception_type == "PORTABLE":
            params.single_earth_station.antenna.gain = 2.14
            params.single_earth_station.antenna.pattern = "OMNI"
        elif bs_reception_type == "MOBILE":
            params.single_earth_station.antenna.gain = 1.14
            params.single_earth_station.antenna.pattern = "OMNI"

        for mss_dc_load in MSS_DC_LOAD_FACTORS:
            for bs_channel, channel_params in BS_CHANNELS.items():
                params.single_earth_station.frequency = channel_params['center_freq_mhz']
                params.imt.bs.load_probability = mss_dc_load

                is_co_channel = True if bs_channel == 62 else False

                if is_co_channel:  # Co-channel scenario
                    params.imt.frequency = channel_params['center_freq_mhz']  # we fix the DC-MSS-IMT DL transmission at the edge of A5 band
                    params.general.enable_adjacent_channel = False # We will set it to True for adjacent channel scenarios in loop below
                    params.general.enable_cochannel = True # We will set it to False for adjacent channel scenarios in loop below

                else:  # Adjacent channel scenario
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

                specific = get_specific_pattern(
                    imt_id, bs_id, mss_dc_load, bs_channel, bs_reception_type
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
