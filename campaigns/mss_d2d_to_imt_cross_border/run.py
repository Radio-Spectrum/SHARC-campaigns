# from sharc.run_multiple_campaigns_mut_thread import run_campaign
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR, ROOT_DIR

CAMPAIGN_NAME = "mss_d2d_to_imt_cross_border"
CAMPAIGN_STR = f"campaigns/{CAMPAIGN_NAME}"

CAMPAIGN_DIR = ROOT_DIR / CAMPAIGN_STR
INPUTS_DIR = CAMPAIGN_DIR / "input/"

def get_output_dir_start(mss_id: str, co_channel: bool):
    return f"output_{mss_id}_{"co" if co_channel else "adj"}"

# if __name__ == "__main__":
#     # Run the campaigns
#     # This function will execute the campaign with the given name.
#     # It will look for the campaign directory under the specified name and
#     # start the necessary processes.
#     run_campaign(CAMPAIGN_NAME)

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import sharc


def _run_command(param_file: Path, main_cli_path: Path) -> int:
    command = [sys.executable, str(main_cli_path), "-p", str(param_file)]
    result = subprocess.run(command, check=False)
    return result.returncode


def run_local_campaign() -> None:
    main_cli_path = Path(sharc.__file__).resolve().parent / "main_cli.py"
    parameter_files = sorted(INPUTS_DIR.glob("*.yaml"))

    if len(parameter_files) == 0:
        raise ValueError(f"No parameter files were found in {INPUTS_DIR}")

    print(f"[INFO] Using local input directory: {INPUTS_DIR}")

    num_threads = min(len(parameter_files), os.cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        return_codes = list(
            executor.map(
                _run_command,
                parameter_files,
                [main_cli_path] * len(parameter_files),
            )
        )

    failures = sum(code != 0 for code in return_codes)
    if failures:
        raise RuntimeError(
            f"{failures} simulation(s) failed. Check logs in output directory."
        )


def main():
    # Sanity check: ensure we have inputs
    if not INPUTS_DIR.exists() or not any(INPUTS_DIR.glob("*.yaml")):
        print(
            f"[ERROR] No input YAMLs found in '{INPUTS_DIR}'. "
        )
        return 2

    print(f"[INFO] Running campaign: {CAMPAIGN_NAME}")
    try:
        run_local_campaign()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        return 130
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
