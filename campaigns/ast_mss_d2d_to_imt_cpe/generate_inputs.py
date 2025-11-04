from itertools import product
from pathlib import Path
from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.ast_mss_d2d_to_imt_cpe.constants import (
    CAMPAIGN_STR, CAMPAIGN_NAME, INPUTS_DIR, PARAMETERS,
    CELL_RADIUS_KM,
    get_specific_pattern, get_readable_from_str
)

SEED = 81

general = {
    "seed": SEED,
    "num_snapshots": int(1e3),
    "overwrite_output": False,
    "output_dir": f"{CAMPAIGN_STR}/output/",
    "output_dir_prefix": "to-update",
    "system": "MSS_D2D",
    "imt_link": "UPLINK",
}


# Generate the parameters for the UE vs CPE campaign
#
# Assumptions for CPE parameters:
# antenna height = 1.5 m
# body loss = 0 dB
# antenna gain = 0 dBi

cpe_params = {
    "antenna_height_m": 1.5,
    "body_loss_db": 0.0,
    "antenna_gain_dbi": 0.0,
}

def generate_inputs():
    """Gera os arquivos YAML de parâmetros"""
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Gerando arquivos em: {INPUTS_DIR}")
    factory = ParametersFactory()

    total = 0

    for (
        imt_ue_type,
        imt_id,
        mss_d2d_id,
        mss_d2d_lf,
        exclusion_margin_km,
    ) in product(*PARAMETERS):

        general["imt_link"] = 'DOWNLINK'  # only uplink for UE/CPE

        print("Generating parameters:")
        print("\timt_link=", general["imt_link"], end=";")
        print("\timt_ue_type=", imt_ue_type, end=";")
        print("\timt_id=", imt_id, end=";")
        print("\tmss_d2d_id=", mss_d2d_id, end=";")
        print("\tmss_d2d_lf=", mss_d2d_lf, end=";")
        print("\texclusion_r_km=", exclusion_margin_km, end=";")

        total += 1

        # Construir objeto de parâmetros
        params = (
            factory
            .load_from_id(imt_id)
            .load_from_id(mss_d2d_id)
            .load_from_dict({"general": general})
            .build()
        )

        # Configurar cenário
        params.general.enable_adjacent_channel = False
        params.general.enable_cochannel = True
        params.imt.interfered_with = True
        params.imt.imt_dl_intra_sinr_calculation_disabled = True

        # CPE-speficic parameters
        if imt_ue_type == "imt-cpe":
            params.imt.ue.body_loss = 0.0
            params.imt.ue.antenna.gain = 0.0
            params.imt.ue.height = 1.5
            params.imt.ue.indoor_percent = 0.0  # all outdoor

        # Frequencies and bandwidths
        params.mss_d2d.bandwidth = 5.0  # MHz
        # Using the LTE-28/A5 frequency arrangement for IMT
        params.imt.frequency = 758 + params.imt.bandwidth / 2
        params.imt.bandwidth = 10.0  # MHz
        # Using the LTE-256/B4 frequency arrangement for IMT
        # params.imt.frequency = 2110 + params.imt.bandwidth / 2
        # params.imt.bandwidth = 20.0  # MHz
        params.mss_d2d.frequency = params.imt.frequency  # full bw overlap
        params.imt.ue.k = 3

        # Adding this just to prevent UserWarnings for unset mask parameters.
        params.mss_d2d.spectral_mask = "MSS"

        # Parameters used for P.619
        # WARNING: Remember to set the lut in propagation/Dataset!
        params.mss_d2d.channel_model = "P619"
        params.mss_d2d.param_p619.earth_station_lat_deg = -25.5549751
        params.mss_d2d.param_p619.earth_station_alt_m = 200
        params.mss_d2d.param_p619.mean_clutter_height = "low"
        # P.619 suggests 3dB polarization loss as good constant value for monte carlo
        params.mss_d2d.polarization_loss = 3.0  # dB

        # DC-MSS load factor
        params.mss_d2d.beams_load_factor = mss_d2d_lf

        # Geometry
        # International Friendship Bridge
        center_lat = -25.5549751
        center_lon = -54.5746686
        params.imt.topology.central_latitude = center_lat
        params.imt.topology.central_longitude = center_lon
        params.imt.topology.central_altitude = 200

        # Beam pointing
        params.mss_d2d.beam_positioning.type = "SERVICE_GRID"
        service_grid = params.mss_d2d.beam_positioning.service_grid
        service_grid.grid_in_zone.type = "FROM_COUNTRIES"
        service_grid.grid_in_zone.from_countries.country_names = [
            "Brazil",
            "Argentina",
        ]
        service_grid.grid_in_zone.from_countries.margin_from_border = exclusion_margin_km

        # Beam is active if satellite
        params.mss_d2d.sat_is_active_if.conditions = [
            "MINIMUM_ELEVATION_FROM_ES",
        ]
        # Set the minimum elevation as the service elevation angle. That way we avoid dealing with multiple patterns
        # according to System 4 specifications.
        params.mss_d2d.sat_is_active_if.minimum_elevation_from_es = 50.0
        # big number to make it so any visible satellite is ellegible
        service_grid.eligible_sats_margin_from_border = -2 * 1110
        # This parameter define the minium elevation angle for the service grid points
        service_grid.minimum_service_angle = 50.0

        # service_grid.grid_in_zone.type = "CIRCLE"
        # service_grid.grid_in_zone.circle.center_lat = center_lat
        # service_grid.grid_in_zone.circle.center_lon = center_lon
        # # grid_radius = float(get_service_zone_radius_from_max_num_of_beams(
        # #     max_n_beams, CELL_RADIUS_KM, exclusion_margin_km
        # # ))
        # # print("grid_radius", grid_radius)
        # service_grid.grid_in_zone.circle.radius_km = 120

        # service_grid.grid_exclusion_zone.type = "FROM_COUNTRIES"
        # service_grid.grid_exclusion_zone.from_countries.country_names = ["Paraguay"]
        # service_grid.grid_exclusion_zone.from_countries.margin_from_border = -exclusion_margin_km

        # Gerar nome do arquivo
        specific = get_specific_pattern(
            imt_ue_type, imt_id, mss_d2d_id, mss_d2d_lf, exclusion_margin_km,
        )

        # Configurar caminhos de saída
        params.general.output_dir_prefix = OUTPUT_START_NAME + specific
        # readable = get_readable_from_str(params.general.output_dir_prefix)
        # print("readable", readable)

        output_path = INPUTS_DIR / f"{PARAMETER_START_NAME}{specific}.yaml"

        # Escrever arquivo YAML
        try:
            dump_parameters(output_path, params)
            print(f"Arquivo gerado: {output_path}")
        except Exception as e:
            print(f"Falha ao gerar {output_path}: {str(e)}")

    print(f"\nTotal de arquivos gerados: {total}\n")


def clear_inputs():
    """Limpa o diretório de entrada antes da geração"""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Limpando diretório: {INPUTS_DIR}")
    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()


if __name__ == "__main__":
    clear_inputs()
    generate_inputs()
