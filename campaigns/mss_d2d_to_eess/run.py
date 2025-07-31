from sharc.run_multiple_campaigns_mut_thread import run_campaign

from campaigns.mss_d2d_to_eess.generate_inputs import clear_inputs, generate_inputs
from campaigns.mss_d2d_to_eess.constants import CAMPAIGN_NAME

if __name__ == "__main__":
    clear_inputs()

    generate_inputs()

    run_campaign(CAMPAIGN_NAME)
