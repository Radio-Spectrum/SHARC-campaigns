from itertools import product
from pathlib import Path
from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.new_mss_d2d.constants import (
    CAMPAIGN_STR, CAMPAIGN_NAME, INPUTS_DIR, PARAMETERS,
    CELL_RADIUS_KM,
    get_specific_pattern, get_readable_from_str
)

SEED = 81

general = {
    "seed": SEED,
    "num_snapshots": int(1e4),
    "overwrite_output": False,
    "output_dir": f"{CAMPAIGN_STR}/output/",
    "output_dir_prefix": "to-update",
    "system": "MSS_D2D",
    "imt_link": "UPLINK",
}

def generate_inputs():
    """Gera os arquivos YAML de parâmetros"""
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Gerando arquivos em: {INPUTS_DIR}")
    factory = ParametersFactory()

    total = 0

    for (imt_link, imt_id, mss_d2d_id,
         mss_d2d_lf, exclusion_margin_km,
         served_countries
    ) in product(*PARAMETERS):
        general["imt_link"] = imt_link.upper()

        print("Gerando:")
        print("\timt_link=", imt_link, end=";")
        print("\timt_id=", imt_id, end=";")
        print("\tmss_d2d_id=", mss_d2d_id, end=";")
        print("\tmss_d2d_lf=", mss_d2d_lf, end=";")
        print("\texclusion_r_km=", exclusion_margin_km, end=";")
        print(f"\t{served_countries=}", end=";")

        # print(f"Gerando: {imt_link} {imt_id}→{mss_d2d_id}, load={mss_d2d_lf}%")
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

        # TODO: choose frequency more carefully
        params.imt.frequency = 758
        params.mss_d2d.frequency = 758

        # Parameters used for P.619
        # WARNING: Remember to set the lut in propagation/Dataset!
        params.mss_d2d.channel_model = "P619"
        params.mss_d2d.param_p619.earth_station_lat_deg = -25.5549751
        params.mss_d2d.param_p619.earth_station_alt_m = 200
        params.mss_d2d.param_p619.mean_clutter_height = "low"

        # Polarization loss - following Item 2.2 of the Rec. ITU-P.61
        params.mss_d2d.polarization_loss = 3.0  # dB

        # Carga da BS
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
        service_grid.transform_grid_randomly = True

        service_grid.grid_in_zone.type = "FROM_COUNTRIES"
        service_grid.grid_in_zone.from_countries.country_names = served_countries
        service_grid.grid_in_zone.from_countries.margin_from_border = exclusion_margin_km

        # Beam is active if satellite
        params.mss_d2d.sat_is_active_if.conditions = [
            "MINIMUM_ELEVATION_FROM_ES",
            "LAT_LONG_INSIDE_COUNTRY",
        ]
        params.mss_d2d.sat_is_active_if.minimum_elevation_from_es = 50.0
        params.mss_d2d.sat_is_active_if.lat_long_inside_country.country_names = \
            service_grid.grid_in_zone.from_countries.country_names
        ###### Calculating margin from border so that satellite will be at
        # most observed from 50deg elevation from border
        # x + 90 + 50 + theta = 180
        # theta = 90 - 50 - x
        # theta = 40 - x

        # (R + h) / sin(90+50) = R / sin(x)
        # sin(x) = sin(90+50) * R / (R + h)
        # x = arcsin(sin(90+50) * R / (R + h))
        # x = 36.5 deg
        # theta = 3.5 deg
        # distance_km = theta_rad * R = 389 km
        params.mss_d2d.sat_is_active_if.lat_long_inside_country.margin_from_border = -389

        # big number to make it so that any visible satellite is ellegible
        service_grid.eligible_sats_margin_from_border = -2 * 1110
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
            imt_link, imt_id, mss_d2d_id, mss_d2d_lf, exclusion_margin_km, served_countries
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
