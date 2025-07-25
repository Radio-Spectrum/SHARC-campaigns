from sharc.run_multiple_campaigns_mut_thread import run_campaign
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

CAMPAIGN_NAME = "mss_d2d_to_imt_cross_border"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

def get_output_dir_start(mss_id: str, co_channel: bool):
    return f"output_{mss_id}_{"co" if co_channel else "adj"}"

if __name__ == "__main__":
    # Run the campaigns
    # This function will execute the campaign with the given name.
    # It will look for the campaign directory under the specified name and
    # start the necessary processes.
    run_campaign(CAMPAIGN_NAME)

