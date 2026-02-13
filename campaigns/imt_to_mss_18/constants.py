from campaigns.utils.constants import SHARC_SIM_ROOT_DIR, ROOT_DIR
from pathlib import Path
import typing
import os

# Path to SHARC simulator - tries multiple methods to find it
def _get_sharc_path():
    """Get SHARC simulator path using multiple fallback methods"""
    # Method 1: Try relative path from campaigns repo (assumes structure: sharc_simulator/SHARC/sharc/)
    campaigns_root = Path(__file__).parents[2].absolute()
    relative_path = campaigns_root.parent / "SHARC" / "sharc"
    if relative_path.exists():
        return relative_path
    
    # Method 2: Try using SHARC_SIM_ROOT_DIR (from installed sharc module)
    if SHARC_SIM_ROOT_DIR.exists():
        return SHARC_SIM_ROOT_DIR
    
    # Method 3: Try environment variable
    env_path = os.getenv("SHARC_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    
    # Method 4: Default fallback (will show warning if doesn't exist)
    return campaigns_root.parent / "SHARC" / "sharc"

SHARC_PATH = _get_sharc_path()

# Path to campaigns repository
MY_CAMPAIGNS_PATH = Path(__file__).parent.absolute()

# Update CAMPAIGN_NAME to match folder name
CAMPAIGN_NAME = "imt_to_mss_18"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

#CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

# Output directory in campaigns repository (not in simulator directory)
OUTPUT_DIR = ROOT_DIR / CAMPAIGN_STR / "output/"

SYS_ID_TO_READABLE = {
    "mss.7300MHz.hubType-18": "Hub Type 18 @7300MHz",
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
    print("OUTPUT_DIR", OUTPUT_DIR)
    print("SHARC_PATH", SHARC_PATH)
    print("MY_CAMPAIGNS_PATH", MY_CAMPAIGNS_PATH)
