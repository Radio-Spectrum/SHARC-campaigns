from campaigns.utils.constants import ROOT_DIR

CAMPAIGN_NAME = "wp4c_oct_26_dc_mss_imt_to_bs"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"
OUTPUT_DIR = CAMPAIGN_DIR / "output/"

# MSS DC as IMT
IMT_MSS_DC_IDS = [
    "imt.698-960MHz.mss-dc.system3-525km",
    "imt.698-960MHz.mss-dc.system3-340km",
    "imt.698-960MHz.mss-dc.system4-690km",
]
MSS_DC_LOAD_FACTORS = [
    0.2,
    0.5,
]
# ES receive frequencies to evaluate with associated offsets (MHz)
# Base frequency: 2162.5 MHz (lower bound of DCM band)
# Variations: 2162.5 - offset values
# All are adjacent-band scenarios
# ES_RX_OFFSETS = [  # (frequency, offset_label, description)
#  #   (2162.5, "offset_0MHz", "nominal - 2162.5 MHz"),
#     (2157.5, "offset_minus5MHz", "2162.5 - 5 MHz"),
#     (2152.5, "offset_minus10MHz", "2162.5 - 10 MHz"),
#     (2147.5, "offset_minus15MHz", "2162.5 - 15 MHz"),
# ]

BS_CHANNELS = {
    51: {
        "center_freq_mhz": 695,
    },
    61: {
        "center_freq_mhz": 755.,
    },
    62: {
        "center_freq_mhz": 761.,
    }
}

# BS victim earth station
BS_IDS = [
    # "bs.582MHz-960MHz.bandV.DVB-T2",
    "bs.582MHz-960MHz.bandV.ISDB-T",
]

# Each BS type has a different antenna. We're adding it here instead
# of creating new from-docs for each one.
BS_REPECTION_TYPE = [
    # "FIXED",
    "PORTABLE",
    "MOBILE",
]


BS_TO_READABLE = {
    "bs.582MHz-960MHz.bandV.DVB-T2": "DVB-T2",
    "bs.582MHz-960MHz.bandV.ISDB-T": "ISDB-T",
}

IMT_MSS_DC_ID_TO_READABLE = {
    "imt.698-960MHz.mss-dc.system3-525km": "SYS3 @525km",
    "imt.698-960MHz.mss-dc.system3-340km": "SYS3 @340km",
    "imt.698-960MHz.mss-dc.system4-690km": "SYS4 @690km"
}


def get_specific_pattern(
    mss_d2d_id: str,
    bs_id: str,
    mss_d2d_load_factor: float,
    bs_channel: int,
    bs_reception_type: str
):
    """
    Generate a pattern string identifying the simulation configuration.
    offset_label: e.g., 'offset_0MHz', 'offset_minus5MHz'
    """
    return f"{mss_d2d_load_factor}load_bs_{bs_id}_channel_{bs_channel}_{bs_reception_type}_mss_d2d_{mss_d2d_id}"


if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)

