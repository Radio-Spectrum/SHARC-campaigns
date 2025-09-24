import argparse

OPTION_TO_SELECTED_SYS = {
    "3.1": ["system-3.2110-2200MHz.525km"],
    "3.2": ["system-3.2110-2200MHz.340km"],
    # "4": ["system-4.2110-2200MHz.690km"],
    "all": [
        "system-3.2110-2200MHz.525km",
        "system-3.2110-2200MHz.340km",
        # "system-4.2110-2200MHz.690km",
    ]
}

OPTION_TO_SELECTED_IMT_DEPLOYMENT = {
    "urban": ["imt.1-3GHz.single-bs.aas-urban-macro-bs"],
    "suburban": ["imt.1-3GHz.single-bs.aas-suburban-macro-bs"],
    "rural": ["imt.1-3GHz.single-bs.aas-rural-macro-bs"],
    "all": [
        "imt.1-3GHz.single-bs.aas-urban-macro-bs",
        "imt.1-3GHz.single-bs.aas-suburban-macro-bs",
        "imt.1-3GHz.single-bs.aas-rural-macro-bs",
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

    supported_imt_deployment = list(OPTION_TO_SELECTED_IMT_DEPLOYMENT.keys())
    parser.add_argument(
        "--imt_deployment",
        type=str,
        choices=supported_imt_deployment,
        default="urban",
        help=f"IMT deployment scenario to use. Choose one of {supported_imt_deployment}"
    )

    return parser
