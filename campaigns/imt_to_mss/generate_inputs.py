from itertools import product

from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters

from campaigns.imt_to_mss.constants import CAMPAIGN_STR, CAMPAIGN_NAME, INPUTS_DIR

SEED = 81

# >>> Choose which clutter variants to generate (ONLY these two values are accepted):
CLUTTER_TYPES = ['both_ends']           # or ['one_end', 'both_ends']

# Allowed values (strict; no synonyms)
ALLOWED_CLUTTER_TYPES = {'one_end', 'both_ends'}

general = {
    "seed": SEED,
    "num_snapshots": 5000,
    "overwrite_output": False,
    "output_dir": f"{CAMPAIGN_STR}/output/",
    "output_dir_prefix": "to-update",
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "UPLINK",
}


def _validate_clutter_types(ct_list):
    """
    Ensure CLUTTER_TYPES is non-empty and contains only allowed values.
    Deduplicate while preserving order.
    """
    if not ct_list:
        raise ValueError("CLUTTER_TYPES must not be empty.")
    invalid = [ct for ct in ct_list if ct not in ALLOWED_CLUTTER_TYPES]
    if invalid:
        raise ValueError(
            f"Invalid clutter_type values: {invalid}. "
            f"Allowed: {sorted(ALLOWED_CLUTTER_TYPES)}"
        )
    seen, result = set(), []
    for ct in ct_list:
        if ct not in seen:
            seen.add(ct)
            result.append(ct)
    return result


def _p_mode_tag(p):
    """Return a filename-safe tag for percentage_p (handles ints and strings)."""
    if isinstance(p, (int, float)):
        return f"{int(p)}"
    return str(p).lower()


def generate_inputs():
    """
    Build and dump parameter YAMLs for the IMT->MSS campaign (strict clutter_type).

    For each combination of:
      - link direction: UPLINK, DOWNLINK
      - IMT system: macrocell (you can re-enable microcell below)
      - MSS system: hubType-18
      - ES y-position: 8 values around Ro
      - BS load probability: 20%
      - P.452 p-mode: 20, RANDOM, RANDOM_GLOBAL
      - clutter_type: values from CLUTTER_TYPES
    """
    OUTPUT_START_NAME = f"output_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"parameter_{CAMPAIGN_NAME}_"

    print(f"Inputs will be written to directory '{INPUTS_DIR}'")

    factory = ParametersFactory()

    # Validate clutter types (strict)
    clutter_types = _validate_clutter_types(CLUTTER_TYPES)

    # ES y-position sweep
    Ro = 1600
    #y_values = [Ro - 600, Ro - 300, Ro, Ro + 300, Ro + 600, Ro + 900, Ro + 1200, Ro + 1500]
    y_values = [Ro + 1000, Ro + 2000, Ro + 5000, Ro + 10000]

    # Percent (converted to fraction for params.imt.bs.load_probability)
    load_probabilities = [20]

    # Two stochastic modes for P.452 clutter percentile p
    p_modes = [20, "RANDOM", "RANDOM_GLOBAL"]

    total = 0

    for imt_link in ["UPLINK", "DOWNLINK"]:
        general["imt_link"] = imt_link
        imt_link_tag = imt_link.lower()

        # Adjust IMT systems here if you want both macro and micro:
        for imt_id in ["imt.7300MHz.macrocell"]:
            for mss_id in ["mss.7300MHz.hubType-18"]:
                for y, load_pct, p_mode, clutter_type in product(
                    y_values, load_probabilities, p_modes, clutter_types
                ):
                    print(
                        f"[Building params for {imt_link} {imt_id} -> {mss_id}, "
                        f"y={y}, load={load_pct}%, p_mode={p_mode}, clutter={clutter_type}]"
                    )
                    total += 1

                    # Load and merge parameter sets
                    params = (
                        factory
                        .load_from_id(imt_id)
                        .load_from_id(mss_id)
                        .load_from_dict({"general": general})
                        .build()
                    )

                    # Scenario toggles
                    params.general.enable_adjacent_channel = False
                    params.general.enable_cochannel = True

                    # IMT is the interferer; disable DL intra-SINR for performance
                    params.imt.interfered_with = False
                    params.imt.imt_dl_intra_sinr_calculation_disabled = True

                    # Fixed Earth Station location (x=0, y varies)
                    params.single_earth_station.geometry.location.type = "FIXED"
                    params.single_earth_station.geometry.location.fixed.x = 0
                    params.single_earth_station.geometry.location.fixed.y = y

                    # BS load as fraction
                    params.imt.bs.load_probability = load_pct / 100.0

                    # P.452 clutter percentile selection mode
                    params.single_earth_station.param_p452.percentage_p = p_mode

                    # P.452 clutter settings (strict)
                    params.single_earth_station.param_p452.clutter_loss = True
                    params.single_earth_station.param_p452.clutter_type = clutter_type  # 'one_end' | 'both_ends'

                    # Output prefix / filename (include p-mode and clutter tags)
                    p_tag = _p_mode_tag(p_mode)
                    specific = (
                        f"{imt_link_tag}_{imt_id}_{mss_id}_y{y}_load{load_pct}"
                        f"_p-{p_tag}_clt-{clutter_type}"
                    ).replace(".", "-")

                    params.general.output_dir_prefix = OUTPUT_START_NAME + specific

                    dump_parameters(
                        INPUTS_DIR / f"{PARAMETER_START_NAME}{specific}.yaml",
                        params,
                    )

    print(f"\nGenerated {total} input YAML scenarios.\n")


def clear_inputs():
    """Ensure the input directory exists and remove any existing YAML files."""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Clearing YAML input files from directory '{INPUTS_DIR}'")
    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()


if __name__ == "__main__":
    clear_inputs()
    generate_inputs()
