from campaigns.utils.constants import SHARC_SIM_ROOT_DIR, ROOT_DIR
import typing

CAMPAIGN_NAME = "imt_to_mss"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
#CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

SYS_ID_TO_READABLE = {
    "mss.7300MHz.hubType-16": "Hub Type 16 @7300MHz",
}

IMT_ID_TO_READABLE = {
    "imt.7300MHz.macrocell": "IMT Macrocell @7300MHz",
    "imt.7300MHz.microcell": "IMT Microcell @7300MHz",
}


def get_specific_pattern(
    topology: typing.Literal["macrocell", "microcell"],
    mss_id: str,
    imt_id: str,
    mask: typing.Literal["imt", "3gpp", "spurious"],
    imt_load_factor: float,
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    if topology not in {"macrocell", "microcell"}:
        raise ValueError(f"Unexpected topology: {topology}")
    
    return f"{mask}_mask_{imt_load_factor}load_{topology}_{imt_id}_{mss_id}"


if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)
