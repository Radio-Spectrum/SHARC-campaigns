from campaigns.utils.constants import SHARC_SIM_ROOT_DIR
import re

CAMPAIGN_NAME = "new_mss_d2d"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

# CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

SYS_IDS = ["system-4.698-960MHz-block1.520km"]
SYS_ID_TO_READABLE = {
    "system-4.698-960MHz-block1.520km": "MSS DC System 4 @700MHz Block 1",
}

IMT_IDS = ["imt.upto-1GHz.single-bs.urban-macro-bs"]
IMT_ID_TO_READABLE = {
    "imt.upto-1GHz.single-bs.urban-macro-bs": "IMT Macro @700MHZ",
}

CELL_RADIUS_KM = 24.105

IMT_LINKS = [
    "downlink",
    # "uplink"
]
MSS_D2D_LOAD_FACTOR = [0.1, 0.2]
EXCLUSION_ZONE_MARGIN_KM = [
    CELL_RADIUS_KM,
    2 * CELL_RADIUS_KM,
    3 * CELL_RADIUS_KM,
    # 4 * CELL_RADIUS_KM,
]

COVERAGE_COUNTRIES = [
    ["Brazil"],
    ["Argentina"],
    ["Brazil", "Argentina"],
]

PARAMETERS = [
    IMT_LINKS,
    IMT_IDS,
    SYS_IDS,
    MSS_D2D_LOAD_FACTOR,
    EXCLUSION_ZONE_MARGIN_KM,
    COVERAGE_COUNTRIES,
]


def get_country_short(c: str):
    if c == "Brazil":
        return "br"
    if c == "Argentina":
        return "ar"

    raise NotImplementedError()

def get_countries_short(cs: list):
    return "_".join([get_country_short(c) for c in cs])

def get_specific_pattern(
    imt_link: str,
    imt_id: str,
    mss_id: str,
    mss_load_factor: float,
    exclusion_r_km: float,
    coverage_countries: list
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    short_countrs = get_countries_short(coverage_countries)
    return f"{short_countrs}_{exclusion_r_km}exclusion_{mss_load_factor}load_{imt_link}_{imt_id}_{mss_id}"

def get_readable(
    imt_link: str,
    imt_id: str,
    mss_d2d_id: str,
    mss_load_factor: float,
    exclusion_r_km: float,
    coverage_countries: list
):
    readable_load = f"LF = {float(mss_load_factor) * 100}%"
    readable_exclusion = f"Excl. R = {exclusion_r_km}km"
    imt_link_readable = "-> IMT UE" if imt_link == "downlink" else "-> IMT BS"
    short_countrs = get_countries_short(coverage_countries)
    readbl_countrs = ", ".join([x.upper() for x in short_countrs.split("_")])

    readable_mss_d2d = SYS_ID_TO_READABLE[mss_d2d_id]
    readable_imt = IMT_ID_TO_READABLE[imt_id]
    return f"{readable_load}; {readable_exclusion}; {imt_link_readable}; {readbl_countrs}"


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

