from campaigns.utils.constants import SHARC_SIM_ROOT_DIR
import typing

CAMPAIGN_NAME = "mss_d2d_to_eess"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

SYS_ID_TO_READABLE = {
    "eess.2200-2290MHz.system-B": "EESS B",
    "eess.2200-2290MHz.system-D": "EESS D",
}

def get_specific_pattern(
    elev: int | typing.Literal["UNIFORM"],
    eess_id: str,
    mask: typing.Literal["mss", "3gpp", "spurious"],
    mss_load_factor: float
):
    if isinstance(elev, int):
        pass
    elif isinstance(elev, str) and elev.lower() == "uniform":
        elev = elev.lower() + "_"
    else:
        raise ValueError(
            f"Unexpected elevation value for pattern: {elev}"
        )
    return f"{mask}_mask_{mss_load_factor}load_{elev}elev_{eess_id}"

if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)
