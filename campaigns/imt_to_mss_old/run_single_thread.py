# run_single.py
from pathlib import Path
import sys

# Make sure SHARC is importable
sharc_root = Path(__file__).resolve().parents[2] / "SHARC"
sys.path.insert(0, str(sharc_root))

from sharc.main_cli import main

if __name__ == "__main__":
    # absolute path to the parameter file you want to run
    param_file = Path(
        r"C:\Users\Daniel\Documents\Git\SHARC\sharc\campaigns\imt_to_mss\input"
        r"\parameter_imt_to_mss_downlink_imt-7300MHz-macrocell_mss-7300MHz-hubType-18_y2600_load50_p-20_clt-both_ends.yaml"
    )

    if not param_file.exists():
        raise FileNotFoundError(f"Parameter file not found: {param_file}")

    print(f"[INFO] Running single simulation with {param_file}")
    # call SHARC CLI main with the parameter file
    main([str(param_file)])
