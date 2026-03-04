from campaigns.utils.constants import SHARC_SIM_ROOT_DIR
import re
import numpy as np

CAMPAIGN_NAME = "system4_mss_d2d_to_imt_pfd"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

# CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

SYS_IDS = [
    "system-4.698-960MHz-block2.690km",
    "system-4.1427-2690MHz.690km"
]

SYS_ID_TO_READABLE = {
    "system-4.698-960MHz-block2.690km": "MSS DC System 4 @690km Block 2",
    "system-4.698-960MHz-block2.690km-antenna-update": "MSS DC System 4 @690km Block 2",
    "system-4.1427-2690MHz.690km": "MSS DC System 4 @2GHz",
}

IMT_IDS = [
    "imt.upto-1GHz.single-bs.urban-macro-bs",
    "imt.1-3GHz.single-bs.aas-macro-bs"
]

IMT_ID_TO_READABLE = {
    "imt.upto-1GHz.single-bs.urban-macro-bs": "IMT Macro @700MHZ",
    "imt.1-3GHz.single-bs.aas-macro-bs": "IMT Macro @2GHz",
}

IMT_LINKS = [
    "downlink",
    "uplink"
]

IMT_UE_TYPE = [
    "imt-ue",
    # "imt-cpe",
]

MSS_D2D_LOAD_FACTOR = [0.2, 0.5]

# Rec. ITU-R M.1036-7 IMT bands - downlink band lower limits
IMT_A5_DL_BAND_LOW_MHZ = 758.0
IMT_B4_DL_BAND_LOW_MHZ = 2110.0
IMT_C1_DL_BAND_LOW_MHZ = 2620.0

IMT_FREQUENCIES_MHZ = [
    IMT_A5_DL_BAND_LOW_MHZ,
    IMT_B4_DL_BAND_LOW_MHZ,
    IMT_C1_DL_BAND_LOW_MHZ,
]

IMT_FREQ_TO_IDS_MAP = {
    IMT_A5_DL_BAND_LOW_MHZ: {"imt_id": "imt.upto-1GHz.single-bs.urban-macro-bs", "mss_id": "system-4.698-960MHz-block2.690km"},
    IMT_B4_DL_BAND_LOW_MHZ: {"imt_id": "imt.1-3GHz.single-bs.aas-macro-bs", "mss_id": "system-4.1427-2690MHz.690km"},
    IMT_C1_DL_BAND_LOW_MHZ: {"imt_id": "imt.1-3GHz.single-bs.aas-macro-bs", "mss_id": "system-4.1427-2690MHz.690km"},
}

POWER_CONTROL_ZONES_STR = """
  power_control_zones:
    zones:
      - power_backoff_db: 0.0
        geometry:
          type: FROM_COUNTRIES
          from_countries:
            country_names:
            - Brazil
            margin_from_border: 150.0
      - power_backoff_db: 10.0
        geometry:
          type: FROM_COUNTRIES
          from_countries:
              country_names:
              - Brazil
              margin_from_border: 0.0
"""

def get_service_zone_radius_from_max_num_of_beams(
    max_num_of_beams,
    cell_radius,
    exclusion_zone_radius,
):
    """Calculates the radius R of the annulus that can contain
    at maximum the number of beams specified
    """
    # Area = n_beams * hexagon_area, so
    A = max_num_of_beams * cell_radius * 3 * np.sqrt(3) / 2
    # A = pi * (R**2 - exclusion_zone_radius**2)
    # so
    R = np.sqrt(A / np.pi + exclusion_zone_radius**2)
    return R


def get_specific_pattern(
    imt_ue_type: str,
    imt_id: str,
    imt_freq_mhz: float,
    mss_id: str,
    beam_elev: float,
    exclusion_r_km: float,
    power_backoff: float,
    lf: float,
    use_phased_array: bool
):
    """
    Generate a pattern string identifying the simulation configuration.
    """
    array_readable = "array" if use_phased_array else "fixed"
    return f"{exclusion_r_km}exclusion_{beam_elev}beam_elev_{power_backoff}power_backoff_{int(lf*100)}load_factor_{imt_ue_type}_{int(imt_freq_mhz)}mhz_{array_readable}_pattern_{imt_id}_{mss_id}"

def get_readable(
    imt_ue_type: str,
    imt_id: str,
    mss_d2d_id: str,
    beam_elev: float,
    exclusion_r_km: float,
    power_backoff: float,
    lf: float,
):
    readable_beam_elev = f"Min. Beam Elev. = {beam_elev}°"
    readable_exclusion = f"Margin = {exclusion_r_km}km"
    imt_ue_type_readable = imt_ue_type
    readable_mss_d2d = SYS_ID_TO_READABLE[mss_d2d_id]
    readable_imt = IMT_ID_TO_READABLE[imt_id]
    # return f"{readable_mss_d2d}; {readable_load}; {readable_exclusion}; {imt_ue_type.upper()}"
    return f"{readable_mss_d2d}; {readable_exclusion}; {readable_beam_elev}; Power Backoff = {power_backoff} dB; Load Factor = {int(lf*100)}%"


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
