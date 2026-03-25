from campaigns.utils.constants import ROOT_DIR

CAMPAIGN_NAME = "mss_d2d_to_mss_adj_study_system_2"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"
OUTPUT_DIR = CAMPAIGN_DIR / "output/"

# MSS DC as IMT
IMT_MSS_DC_IDS = [
    "imt.1805-1920MHz.2110-2170MHz.mss-dc.system2-500km",
]
MSS_DC_LOAD_FACTORS = [
    0.2,
    0.5,
]
# ES receive frequencies to evaluate with associated offsets (MHz)
# Base frequency: 2162.5 MHz (lower bound of DCM band)
# Variations: 2162.5 - offset values
# All are adjacent-band scenarios
initial_frequency_MHz = 2120.0  # MHz
steps = 1.25

freq_1 = initial_frequency_MHz +  steps/2
freq_2 = freq_1 + 5
freq_3 = freq_2 + 5 

ES_RX_OFFSETS = [ 
    (freq_1, "First Adjacent Channel", f"{freq_1} MHz"),
    (freq_2, "Second Adjacent Channel", f"{freq_2} MHz"),
    (freq_3, "Third Adjacent Channel", f"{freq_3} MHz"),
]

print("ES_RX_OFFSETS", ES_RX_OFFSETS)
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
    "imt.1805-1920MHz.2110-2170MHz.mss-dc.system2-500km": "System 2 MSS DC @500km",
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

