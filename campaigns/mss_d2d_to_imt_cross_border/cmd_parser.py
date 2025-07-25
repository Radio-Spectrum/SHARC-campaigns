import argparse

OPTION_TO_SELECTED_SYS = {
    "A": ["system-3.2110-2200MHz.525km"],
    "3": ["system-3.2110-2200MHz.340km"],
    "4": ["system-4.2110-2200MHz.690km"],
    "all": [
        "system-3.2110-2200MHz.525km",
        "system-4.2110-2200MHz.690km",
        "system-3.2110-2200MHz.340km",
    ]
}

def sys_alias_to_id(alias):
    try:
        return OPTION_TO_SELECTED_SYS[alias]
    except KeyError:
        raise argparse.ArgumentTypeError(
            f"Invalid alias '{alias}'. Choose from {list(OPTION_TO_SELECTED_SYS.keys())}"
        )

def get_cmd_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MSS D2D to IMT cross border")

    parser.add_argument(
        "--adj",
        action="store_true",
        help="Whether to use only adjacent channel (true/false). Default: false",
    )

    supported_mss_sys_name = list(OPTION_TO_SELECTED_SYS.keys())
    parser.add_argument(
        "--mss",
        type=sys_alias_to_id,
        default="all",
        help=f"Name of mss system to use. Choose one of {supported_mss_sys_name}"
    )

    return parser
