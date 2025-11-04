from pathlib import Path
import sharc

ROOT_DIR = Path(__file__).parents[2].absolute()
ROOT_PARAMS_DIR = ROOT_DIR / "from-docs"
SHARC_SIM_ROOT_DIR = Path(sharc.__file__).parents[0]

if __name__ == "__main__":
    print("ROOT_DIR", ROOT_DIR)
    print("ROOT_PARAMS_DIR", ROOT_PARAMS_DIR)
    print("SHARC_SIM_ROOT_DIR", SHARC_SIM_ROOT_DIR)
