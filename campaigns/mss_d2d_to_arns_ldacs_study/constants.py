from campaigns.utils.constants import ROOT_DIR

CAMPAIGN_NAME = "mss_d2d_to_arns_ldacs_study"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"
OUTPUT_DIR = CAMPAIGN_DIR / "output/"

# MSS DC as IMT
IMT_MSS_DC_IDS = [
    #"imt.2300-2690MHz.mss-dc.system3-525km",
    #"imt.2300-2690MHz.mss-dc.system3-340km",
    "imt.694-960MHz.mss-dc.system4-690km",
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


# MSS victim earth station/user terminal
SINGLE_ES_MSS_IDS = [

    "arns.962MHz.ldacs"
    #"arns.2700MHz.radar"
    #"mss.2500MHz.hibleo-x",
    #"mss.2500MHz.hibleo-xl-1",
    #"mss.2500MHz.ast-ng-c-3",

    # "mss.2100MHz.7.1.4-forward-R",  # 2100 MHz band systems
    # "mss.2100MHz.7.1.5-ES-type-2",
    # "mss.2100MHz.7.1.5-ES-type-1"
]

MSS_ES_TO_READABLE = {
    "arns.962MHz.ldacs": "LDACS"
    #"arns.2700MHz.radar": "Radar"
    # "mss.2500MHz.hibleo-x": "Hibleo-X",
    # "mss.2500MHz.hibleo-xl-1": "Hibleo-XL-1",
    #"mss.2500MHz.ast-ng-c-3": "AST-NG-C-3",

    # "mss.2100MHz.7.1.4-forward-R": "7.1.4_forward-R",  # 2100 MHz band systems
    # "mss.2100MHz.7.1.5-ES-type-2": "ES_type-2",
    # "mss.2100MHz.7.1.5-ES-type-1": "ES_type-1"

}

IMT_MSS_DC_ID_TO_READABLE = {
    #"imt.2300-2690MHz.mss-dc.system3-525km": "MSS DC @525km",
    #"imt.2300-2690MHz.mss-dc.system3-340km": "MSS DC @340km",
    "imt.694-960MHz.mss-dc.system4-690km": "SYS4 @690km"
    
    
}


OFFSET_LABELS = [
    "offset_0MHz",
    "offset_5MHz",
    "offset_10MHz",
    "offset_120MHz"
]

OFFSET_LABELS_READABLE = {
    "offset_0MHz": "First adjacent",
    "offset_5MHz": "Second adjacent",
    "offset_10MHz": "Third adjacent",
    "offset_120MHz": "Spurious domain",
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

