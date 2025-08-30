from campaigns.utils.constants import SHARC_SIM_ROOT_DIR
from warnings import warn

CAMPAIGN_NAME = "mss_d2d_to_mss"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

# MSS DC as IMT
warn("IMT DCs used are not actually proper for current use case")
# NOTE: Parameters @2.5GHz may not be all equal...
# tx power is definitely different (2dB diff)
IMT_MSS_DC_IDS = [
    "imt.2110-2200MHz.mss-dc.system3-525km",
    "imt.2110-2200MHz.mss-dc.system3-340km",
]
MSS_DC_LOAD_FACTORS = [
    0.2,
    0.5,
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
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    return f"{mss_d2d_load_factor}load_es_{mss_es_id}_mss_d2d_{mss_d2d_id}"


if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)

