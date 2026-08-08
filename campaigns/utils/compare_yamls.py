import yaml
from pathlib import Path

def compare_yamls(f1: Path | str, f2: Path | str):
    with open(f1, "r") as f:
        d1 = yaml.safe_load(f)
    with open(f2, "r") as f:
        d2 = yaml.safe_load(f) 

    return compare_dicts(d1, d2)

def compare_dicts(
    d1: dict, d2: dict
) -> dict:
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        return d1 != d2

    res = {}
    for k, v in d1.items():
        if k not in d2:
            res["[-] " + k] = v
    for k, v in d2.items():
        if k not in d1:
            res["[+] " + k] = v
        else:
            if not isinstance(v, dict) or not isinstance(d1[k], dict):
                has_changed = compare_literals(d1[k], v)
                if has_changed:
                    res["[M] " + k] = f"{d1[k]} -> {v}"
            else:
                comparison = compare_dicts(d1[k], v)
                if len(comparison) != 0:
                    res[k] = comparison

    return res

def compare_literals(l1, l2) -> bool:
    """
    Returns true if l1 and l2 are different
    """
    # array is not really a literal but...
    # since we don't have many parameters using array
    # (only one as far as this was done)
    # the return will only be a bool instead of detailed
    # information as done for dict
    if isinstance(l1, list) and isinstance(l2, list):
        if len(l2) != len(l1):
            return False
        for i in range(len(l1)):
            if compare_literals(l1[i], l2[i]):
                return True
        return False

    return l1 != l2

if __name__ == "__main__":
    # Register a tuple constructor with PyYAML
    def tuple_constructor(loader, node):
        """Load the sequence of values from the YAML node and returns a tuple constructed from the sequence."""
        values = loader.construct_sequence(node)
        return tuple(values)


    yaml.SafeLoader.add_constructor(
        'tag:yaml.org,2002:python/tuple',
        tuple_constructor)

    base = "/home/artistreak/Downloads/"
    base1 = "/home/artistreak/projects/Radio-Spectrum/server/multiple_mss_dc_to_imt/"
    f1 = f"{base}parameter_system-3.2110-2200MHz.525km_co_mss_d2d_to_imt_cross_border_40.0km_0.2load_dl.yaml"
    f2 = f"{base1}parameter_multiple_mss_dc_to_imt_ar_39.684exclusion_0.2load_downlink_imt.1-3GHz.single-bs.aas-macro-bs_system-3.2110-2200MHz.525km.yaml"
    comparison = compare_yamls(f1, f2)
    # print(comparison)
    with open(f"comparison.yaml", "w") as f:
        yaml.dump(comparison, f)

    # for elev in [5, 30, 60, 90, "uniform_"]:
    #     f1 = f"/home/artistreak/projects/Radio-Spectrum/SHARC/sharc/campaigns/mss_d2d_to_eess/input/parameters_mss_d2d_to_eess_{elev}elev_system_b.yaml"
    #     f2 = f"/home/artistreak/projects/Radio-Spectrum/SHARC/sharc/campaigns/mss_d2d_to_eess/input/parameter_mss_d2d_to_eess_{elev}elev_eess.2200-2290MHz.system-B.yaml"
    #     comparison = compare_yamls(f1, f2)
    #     # print(comparison)
    #     with open(f"cmps/sys-B-{elev}elev.yaml", "w") as f:
    #         yaml.dump(comparison, f)
    #     f1 = f"/home/artistreak/projects/Radio-Spectrum/SHARC/sharc/campaigns/mss_d2d_to_eess/input/parameters_mss_d2d_to_eess_{elev}elev_system_d.yaml"
    #     f2 = f"/home/artistreak/projects/Radio-Spectrum/SHARC/sharc/campaigns/mss_d2d_to_eess/input/parameter_mss_d2d_to_eess_{elev}elev_eess.2200-2290MHz.system-D.yaml"
    #     comparison = compare_yamls(f1, f2)
    #     # print(comparison)
    #     with open(f"cmps/sys-D-{elev}elev.yaml", "w") as f:
    #         yaml.dump(comparison, f)
