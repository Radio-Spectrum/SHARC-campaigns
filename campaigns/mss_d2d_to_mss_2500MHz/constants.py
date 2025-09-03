from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

CAMPAIGN_NAME = "mss_d2d_to_mss_2500MHz"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

# MSS DC as IMT
IMT_MSS_DC_IDS = [
    "imt.2300-2690MHz.mss-dc.system3-525km",
    "imt.2300-2690MHz.mss-dc.system3-340km",
]
MSS_DC_LOAD_FACTORS = [
    0.1,
    # 0.2,
    # 0.5,
]
USE_RANDOM_GRID_TRANSFORMATION = [
    True,
    False,
]
# MSS victim earth station/user terminal
SINGLE_ES_MSS_IDS = [
    "mss.2500MHz.hibleo-x",
    "mss.2500MHz.hibleo-xl-1",
    "mss.2500MHz.ast-ng-c-3",
]

MSS_ES_TO_READABLE = {
    "mss.2500MHz.hibleo-x": "Hibleo-X",
    "mss.2500MHz.hibleo-xl-1": "Hibleo-XL-1",
    "mss.2500MHz.ast-ng-c-3": "AST-NG-C-3",
}

IMT_MSS_DC_ID_TO_READABLE = {
    "imt.2110-2200MHz.mss-dc.system3-525km": "MSS DC @525km",
    "imt.2110-2200MHz.mss-dc.system3-340km": "MSS DC @340km",
}


def get_specific_pattern(
    mss_d2d_id: str,
    mss_es_id: str,
    mss_d2d_load_factor: float,
    use_random_grid_transf: bool,
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    grid_used = "static"
    if use_random_grid_transf:
        grid_used = "rand"

    return f"{mss_d2d_load_factor}load_{grid_used}_grid_es_{mss_es_id}_mss_d2d_{mss_d2d_id}"


if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)

