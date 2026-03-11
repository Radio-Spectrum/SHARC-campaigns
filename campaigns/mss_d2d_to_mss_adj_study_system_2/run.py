import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import sharc
from campaigns.mss_d2d_to_mss_adj_study_system_2.constants import CAMPAIGN_NAME, INPUTS_DIR
from campaigns.mss_d2d_to_mss_adj_study_system_2.generate_inputs import (
    clear_inputs,
    generate_inputs,
)


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
    parser = argparse.ArgumentParser(
        description="MSS D2D to MSS campaign runner"
    )
    parser.add_argument(
        "-dg", "--dont-generate",
        action="store_true",
        help=(
            "Skip generating input parameter files before running "
            "(default: generate inputs)."
        ),
    )
    args = parser.parse_args()

    if not args.dont_generate:
        # TODO: add unit testing to campaigns?
        # test_calculate_equivalent_acs()
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
