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

MSS_ID_TO_READABLE = {
    "imt.1427-2690MHz.mss-dc.system4-690km": "SYS4 BLOCK2 @620km",
    "imt.2110-2200MHz.mss-dc.system3-525km": "SYS3 @525km",
    "imt.2110-2200MHz.mss-dc.system3-340km": "SYS3 @340km",
}

def get_specific_pattern(
    elev: int | typing.Literal["UNIFORM"],
    eess_id: str,
    imt_mss_dc_id: str,
    channel: typing.Literal["first_adj", "second_adj"],
    excl_radius_km: float,
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
    excl_readius_readable = "0.0km" if excl_radius_km < 0.1 else f"{excl_radius_km:.2f}km"
    return f"{channel}_{f"{excl_radius_km:.2f}"}km_exclusion_{mss_load_factor}load_{elev}elev_{eess_id}_{imt_mss_dc_id}"

if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)
