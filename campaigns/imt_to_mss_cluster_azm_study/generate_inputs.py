from itertools import product
from pathlib import Path
from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.imt_to_mss_cluster_azm_study.constants import CAMPAIGN_STR, CAMPAIGN_NAME, INPUTS_DIR
import math 

SEED = 83

# Configurações
CLUTTER_TYPES = [ 'both_ends']
ALLOWED_CLUTTER_TYPES = { 'both_ends'}

general = {
    "seed": SEED,
    "num_snapshots": 100000,
    "overwrite_output": False,
    "output_dir": f"{CAMPAIGN_STR}/output/",
    "output_dir_prefix": "study-pos-fixed", 
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "UPLINK",
}

def _validate_clutter_types(ct_list):
    """Valida os tipos de clutter"""
    if not ct_list:
        raise ValueError("CLUTTER_TYPES não pode ser vazio")
    invalid = [ct for ct in ct_list if ct not in ALLOWED_CLUTTER_TYPES]
    if invalid:
        raise ValueError(f"Valores inválidos para clutter_type: {invalid}. Permitidos: {sorted(ALLOWED_CLUTTER_TYPES)}")
    seen, result = set(), []
    for ct in ct_list:
        if ct not in seen:
            seen.add(ct)
            result.append(ct)
    return result

def _sanitize_for_filename(s: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo"""
    s = s.replace(" ", "-").replace(".", "-").replace("/", "-").replace("\\", "-")
    keep = "-_()[]{}+,=@"
    return "".join(ch if ch.isalnum() or ch in keep else "-" for ch in s)

def _p_mode_tag(p):
    """
    Gera tag simplificada para nome de arquivo:
    """
    if isinstance(p, (int, float)):
        # Usa _ para evitar problemas com pontos em nomes de arquivo
        return f"{p}".replace(".", "_")
    return str(p).lower()

def calculate_coords(R, angle_deg):
    """
    Calcula x e y em coordenadas cartesianas a partir de R e Azimute (Norte=0°, Leste=90°).
    O centro do cluster IMT é (0, 0).
    """
    angle_rad = math.radians(90 - angle_deg)
    
    x = R * math.cos(angle_rad)
    y = R * math.sin(angle_rad)
    x = round(x, 3)
    y = round(y, 3)
    
    return x, y


def generate_inputs():
    """Gera os arquivos YAML de parâmetros"""
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Gerando arquivos em: {INPUTS_DIR}")
    factory = ParametersFactory()
    clutter_types = _validate_clutter_types(CLUTTER_TYPES)

    # Parâmetros da campanha
    Ro = 1600
    R_values = [Ro + 1500, Ro + 2000, Ro + 5000 ]
    load_probabilities = [50]
    p_modes = ["RANDOM_CENARIO"]
    
    azimuth_pos_values = [0, 90, 180] 
    
    total = 0

    for imt_link in ["DOWNLINK"]:
        general["imt_link"] = imt_link
        imt_link_tag = imt_link.lower()

        for imt_id in ["imt.7300MHz.macrocell"]:
            for mss_id in ["mss.7300MHz.hubType-18"]:
                
                for R, load_pct, p_mode, clutter_type, angle_deg in product(
                    R_values, load_probabilities, p_modes, clutter_types, azimuth_pos_values
                ):
                    x, y = calculate_coords(R, angle_deg)
                    
                    print(
                        f"Gerando: {imt_link} {imt_id}→{mss_id}, R={R}, load={load_pct}%, p={p_mode}, "
                        f"clutter={clutter_type}, Posição Fixa: {angle_deg}° (x={x}, y={y})"
                    )
                    total += 1

                    # Construir objeto de parâmetros
                    params = (
                        factory
                        .load_from_id(imt_id)
                        .load_from_id(mss_id)
                        .load_from_dict({"general": general})
                        .build()
                    )

                    # Configurar cenário
                    params.general.enable_adjacent_channel = False
                    params.general.enable_cochannel = True
                    params.imt.interfered_with = False
                    params.imt.imt_dl_intra_sinr_calculation_disabled = True

                    params.single_earth_station.geometry.location.type = "FIXED"
                    params.single_earth_station.geometry.location.fixed.x = x
                    params.single_earth_station.geometry.location.fixed.y = y
                   
                    # Azimute do cluster: Mantém o apontamento para o centro do cluster IMT (original)
                    params.single_earth_station.geometry.azimuth.type = "POINTING_AT_IMT_CENTER"

                    # Carga da BS
                    params.imt.bs.load_probability = load_pct / 100.0

                    # Configurar parâmetros P.452
                    p_tag= _p_mode_tag(p_mode) if isinstance(p_mode, (int, float)) else p_mode
                    params.single_earth_station.param_p452.percentage_p = p_mode
                    params.single_earth_station.param_p452.clutter_loss = True
                    params.single_earth_station.param_p452.clutter_type = clutter_type

                    # Gerar nome do arquivo
                    specific = (
                        f"{imt_link_tag}_{imt_id}_{mss_id}_R{R}_load{load_pct}"
                        f"_p-{p_tag}_clt-{clutter_type}_pos{angle_deg}" 
                    )
                    specific = _sanitize_for_filename(specific)

                    # Configurar caminhos de saída
                    params.general.output_dir_prefix = OUTPUT_START_NAME + specific
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