from campaigns.utils.constants import SHARC_SIM_ROOT_DIR
import re

CAMPAIGN_NAME = "multiple_mss_dc_to_imt"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

# CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

CENTER_FREQUENCY = 758.0
# CENTER_FREQUENCY = 2160.0
if CENTER_FREQUENCY == 758.0:
    SYS_IDS = [
        "system-3.698-960MHz.525km",
        "system-4.698-960MHz-block2.690km",
    ]
else:
    SYS_IDS = [
        "system-3.2110-2200MHz.525km",
        "system-4.2110-2200MHz.690km",
    ]

SYS_ID_TO_READABLE = {
    "system-4.2110-2200MHz.690km": "MSS DC System 4 @2100MHz",
    "system-3.2110-2200MHz.525km": "MSS DC System 3 @2100MHz",
    "system-3.698-960MHz.525km": "MSS DC System 3 @758MHz",
    "system-4.698-960MHz-block2.690km": "MSS DC System 4 @758MHz",
}

if CENTER_FREQUENCY == 758.0:
    IMT_IDS = [
        "imt.upto-1GHz.single-bs.urban-macro-bs"
    ]
else:
    IMT_IDS = [
        "imt.1-3GHz.single-bs.aas-macro-bs",
    ]

IMT_ID_TO_READABLE = {
    "imt.1-3GHz.single-bs.aas-macro-bs": "IMT Macro @2100MHz",
    "imt.upto-1GHz.single-bs.urban-macro-bs": "IMT Macro @758MHZ",
}

CELL_RADIUS_SYS3_KM = 39.684
if CENTER_FREQUENCY == 2160.0:
    CELL_RADIUS_SYS4_KM = 10.960
else:
    CELL_RADIUS_SYS4_KM = 22.335

IMT_LINKS = [
    "downlink",
    # "uplink"
]
MSS_D2D_LOAD_FACTOR = [0.5, 0.2, 0.1]
EXCLUSION_ZONE_SYS4_MARGIN_KM = [
    40,
    # rounding to get rid of weird precision errors
    # round(2 * CELL_RADIUS_SYS4_KM, 1),
    # round(3 * CELL_RADIUS_SYS4_KM, 1),
]
EXCLUSION_ZONE_SYS3_MARGIN_KM = [
    40,
    # round(2 * CELL_RADIUS_SYS3_KM, 1),
    # round(3 * CELL_RADIUS_SYS3_KM, 1),
]
EXCLUSION_ZONE_MARGIN_KM = list(set(EXCLUSION_ZONE_SYS3_MARGIN_KM + EXCLUSION_ZONE_SYS4_MARGIN_KM))

COVERAGE_COUNTRIES = [
    "Brazil",
    "Argentina",
]

PARAMETERS = [
    IMT_LINKS,
    IMT_IDS,
    SYS_IDS,
    MSS_D2D_LOAD_FACTOR,
    EXCLUSION_ZONE_MARGIN_KM,
    COVERAGE_COUNTRIES,
]

def skip_parameters_combination(
    imt_link,
    imt_id,
    sys_id,
    mss_d2d_load_factor,
    exclusion_zone_margin_km,
    coverage_country,
):
    if "system-3" in sys_id:
        if exclusion_zone_margin_km not in EXCLUSION_ZONE_SYS3_MARGIN_KM:
            # only generate parameter for sys3 correct margin border values
            return True
        # if coverage_country != "Brazil":
        #     # only generate parameter for sys3 covering Brazil
        #     return True
    elif "system-4" in sys_id:
        if exclusion_zone_margin_km not in EXCLUSION_ZONE_SYS4_MARGIN_KM:
            # only generate parameter for sys4 correct margin border values
            return True
        # if coverage_country != "Argentina":
        #     # only generate parameter for sys4 covering Argentina
        #     return True
    else:
        raise NotImplementedError()

    return False


def get_country_short(c: str):
    if c == "Brazil":
        return "br"
    if c == "Argentina":
        return "ar"

    raise NotImplementedError()

def get_specific_pattern(
    imt_link: str,
    imt_id: str,
    mss_id: str,
    mss_load_factor: float,
    exclusion_r_km: float,
    coverage_country: list
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    short_countrs = get_country_short(coverage_country)
    return f"{short_countrs}_{exclusion_r_km}exclusion_{mss_load_factor}load_{imt_link}_{imt_id}_{mss_id}"

def get_readable(
    imt_link: str,
    imt_id: str,
    mss_d2d_id: str,
    mss_load_factor: float,
    exclusion_r_km: float,
    coverage_country: str
):
    readable_load = f"LF = {float(mss_load_factor) * 100}%"
    readable_exclusion = f"Excl. R = {exclusion_r_km}km"
    imt_link_readable = "-> IMT UE" if imt_link == "downlink" else "-> IMT BS"
    short_countrs = get_country_short(coverage_country)
    readbl_countrs = ", ".join([x.upper() for x in short_countrs.split("_")])

    readable_mss_d2d = SYS_ID_TO_READABLE[mss_d2d_id]
    readable_imt = IMT_ID_TO_READABLE[imt_id]
    return f"{readable_load}; {readbl_countrs}; {readable_mss_d2d}"


def get_readable_from_str(
    value: str
):
    """
    Generate a readable format for the specific pattern
    """
    pattern = "(?P<exclusion_r_km>.*)exclusion_(?P<mss_load_factor>.*)load_(?P<imt_link>(up|down)link)_(?P<imt_and_sys_ids>.*)"
    # pattern = ".*mss_d2d_(?P<max_num_of_beams>.*)max_beams_(?P<exclusion_r_km>.*)exclusion_(?P<mss_load_factor>.*)load_(?P<imt_link>(up|down)link)_(?P<imt_and_sys_ids>.*)"
    match = re.search(
        pattern,
        value
    )

    mss_load_factor = match.group("mss_load_factor")

    exclusion_r_km = match.group("exclusion_r_km")


    imt_link = match.group("imt_link")

    imt_and_sys_ids = match.group("imt_and_sys_ids")
    mss_d2d_id = [id for id in SYS_IDS if id in imt_and_sys_ids][0]

    imt_id = [id for id in IMT_IDS if id in imt_and_sys_ids][0]

    return get_readable(
        imt_link,
        imt_id,
        mss_d2d_id,
        mss_load_factor,
        exclusion_r_km,
    )


if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)

