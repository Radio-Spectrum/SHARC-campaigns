from campaigns.utils.constants import SHARC_SIM_ROOT_DIR
import typing

CAMPAIGN_NAME = "mss_d2d_to_mss"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

SYS_ID_TO_READABLE = {
    "mss.7300MHz.hubType-16": "Hub Type 16 @7300MHz",
}

IMT_ID_TO_READABLE = {
    "imt.7300MHz.macrocell": "IMT Macrocell @7300MHz",
    "imt.7300MHz.microcell": "IMT Microcell @7300MHz",
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

