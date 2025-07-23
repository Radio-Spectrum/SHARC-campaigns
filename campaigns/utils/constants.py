from pathlib import Path

ROOT_DIR = Path(__file__).parents[2].absolute()
ROOT_PARAMS_DIR = ROOT_DIR / "from-docs"

if __name__ == "__main__":
    print("ROOT_DIR", ROOT_DIR)
    print("ROOT_PARAMS_DIR", ROOT_PARAMS_DIR)
