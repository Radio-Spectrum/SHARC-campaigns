import argparse
import sys
from sharc.run_multiple_campaigns_mut_thread import run_campaign

from campaigns.mss_d2d_to_mss_2500MHz.generate_inputs import clear_inputs, generate_inputs, test_calculate_equivalent_acs
from campaigns.mss_d2d_to_mss_2500MHz.constants import CAMPAIGN_NAME, INPUTS_DIR

def main():
    parser = argparse.ArgumentParser(description="MSS D2D to MSS campaign runner")
    parser.add_argument(
        "-dg", "--dont-generate",
        action="store_true",
        help="Skip generating input parameter files before running (default: generate inputs).",
    )
    args = parser.parse_args()

    if not args.dont_generate:
        # TODO: add unit testing to campaigns?
        test_calculate_equivalent_acs()
        clear_inputs()
        generate_inputs()
    else:
        # Sanity check: if skipping generation, ensure we have inputs
        if not INPUTS_DIR.exists() or not any(INPUTS_DIR.glob("*.yaml")):
            print(
                f"[ERROR] No input YAMLs found in '{INPUTS_DIR}'. "
                "Remove --dont-generate or run the generator first."
            )
            return 2

    print(f"[INFO] Running campaign: {CAMPAIGN_NAME}")
    try:
        run_campaign(CAMPAIGN_NAME)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        return 130
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
