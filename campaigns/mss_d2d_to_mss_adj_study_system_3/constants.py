from campaigns.utils.constants import ROOT_DIR

CAMPAIGN_NAME = "mss_d2d_to_mss_adj_study_system_3"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"
OUTPUT_DIR = CAMPAIGN_DIR / "output/"

# MSS DC as IMT
IMT_MSS_DC_IDS = [
    "imt.2300-2690MHz.mss-dc.system3-525km",
    "imt.2300-2690MHz.mss-dc.system3-340km",
]
MSS_DC_LOAD_FACTORS = [
    0.2,
    0.5,
]
# ES receive frequencies to evaluate with associated offsets (MHz)
# Base frequency: 2162.5 MHz (lower bound of DCM band)
# Variations: 2162.5 - offset values
# All are adjacent-band scenarios
ES_RX_OFFSETS = [  # (frequency, offset_label, description)
 #   (2162.5, "offset_0MHz", "nominal - 2162.5 MHz"),
    (2157.5, "offset_minus5MHz", "2162.5 - 5 MHz"),
    (2152.5, "offset_minus10MHz", "2162.5 - 10 MHz"),
    (2147.5, "offset_minus15MHz", "2162.5 - 15 MHz"),
]

# MSS victim earth station/user terminal
SINGLE_ES_MSS_IDS = [
    "mss.2100MHz.7.1.4-forward-R",
    "mss.2100MHz.7.1.5-ES-type-1",
    "mss.2100MHz.7.1.5-ES-type-2",
]

MSS_ES_TO_READABLE = {
    "mss.2100MHz.7.1.4-forward-R": "System R (Forward)",
    "mss.2100MHz.7.1.5-ES-type-1": "ES Type-1 (G=2dBi)",
    "mss.2100MHz.7.1.5-ES-type-2": "ES Type-2 (G=10dBi)",
}

IMT_MSS_DC_ID_TO_READABLE = {
    "imt.2300-2690MHz.mss-dc.system3-525km": "MSS DC @525km",
    "imt.2300-2690MHz.mss-dc.system3-340km": "MSS DC @340km",
}


def get_specific_pattern(
    mss_d2d_id: str,
    mss_es_id: str,
    mss_d2d_load_factor: float,
    offset_label: str,
):
    """
    Generate a pattern string identifying the simulation configuration.
    offset_label: e.g., 'offset_0MHz', 'offset_minus5MHz'
    """
    return f"{mss_d2d_load_factor}load_{offset_label}_es_{mss_es_id}_mss_d2d_{mss_d2d_id}"


if __name__ == "__main__":
    print("CAMPAIGN_NAME", CAMPAIGN_NAME)
    print("CAMPAIGN_STR", CAMPAIGN_STR)
    print("CAMPAIGN_DIR", CAMPAIGN_DIR)
    print("INPUTS_DIR", INPUTS_DIR)

