import argparse

from sharc.run_multiple_campaigns_mut_thread import run_campaign

from campaigns.mss_d2d_to_eess.generate_inputs import clear_inputs, generate_inputs
from campaigns.mss_d2d_to_eess.constants import CAMPAIGN_NAME

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MSS D2D to EESS cli")

    parser.add_argument(
        "-dg", "--dont-generate",
        action="store_true",
        help="Flag to not generate parameters before running (true/false). Default: false",
    )

    args = parser.parse_args()
    if not args.dont_generate:
        clear_inputs()
        generate_inputs()

    run_campaign(CAMPAIGN_NAME)
