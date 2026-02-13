from itertools import product
from pathlib import Path
from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.imt_to_mss_18.constants import CAMPAIGN_STR, CAMPAIGN_NAME, INPUTS_DIR, OUTPUT_DIR

SEED = 83

# Configuration
CLUTTER_TYPES = ['both_ends']
ALLOWED_CLUTTER_TYPES = {'one_end', 'both_ends'}

general = {
    "seed": SEED,
    "num_snapshots": 100000,
    "overwrite_output": False,
    "output_dir": str(OUTPUT_DIR),  # Use absolute path to campaigns repository output directory
    "output_dir_prefix": "study-azm-cluster",
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "UPLINK",
}

def _validate_clutter_types(ct_list):
    """Validates clutter types"""
    if not ct_list:
        raise ValueError("CLUTTER_TYPES cannot be empty")
    invalid = [ct for ct in ct_list if ct not in ALLOWED_CLUTTER_TYPES]
    if invalid:
        raise ValueError(f"Invalid values for clutter_type: {invalid}. Allowed: {sorted(ALLOWED_CLUTTER_TYPES)}")
    seen, result = set(), []
    for ct in ct_list:
        if ct not in seen:
            seen.add(ct)
            result.append(ct)
    return result

def _sanitize_for_filename(s: str) -> str:
    """Removes invalid characters for file names"""
    s = s.replace(" ", "-").replace(".", "-").replace("/", "-").replace("\\", "-")
    keep = "-_()[]{}+,=@"
    return "".join(ch if ch.isalnum() or ch in keep else "-" for ch in s)

def _p_mode_tag(p):
    """
    Generates simplified tag for file name:
      - 0.2 → '0.2'
      - 20 → '20'
      - RANDOM_CENARIO → 'RANDSCEN'
      - Other strings remain unchanged
    """
    if isinstance(p, (int, float)):
        # Keep the original format without conversions
        return f"{p}".replace(".", "_")  # Use _ to avoid problems with dots in file names
    p_str = str(p).upper()
    # Map common p_mode values to shorter tags
    if p_str == "RANDOM_CENARIO":
        return "RANDSCEN"
    return str(p).lower()

def _shorten_imt_id(imt_id: str) -> str:
    """Extract short name from IMT ID: 'imt.7300MHz.macrocell' -> 'macro'"""
    parts = imt_id.split('.')
    if not parts:
        return imt_id
    last_part = parts[-1]
    # Convert 'macrocell' to 'macro', 'microcell' to 'micro', etc.
    if last_part == "macrocell":
        return "macro"
    elif last_part == "microcell":
        return "micro"
    return last_part

def _shorten_mss_id(mss_id: str) -> str:
    """Extract short name from MSS ID: returns empty string (not used in filename)"""
    return ""  # Don't include MSS ID in filename

def _shorten_link_tag(link: str) -> str:
    """Convert link direction to short tag: 'DOWNLINK' -> 'dl', 'UPLINK' -> 'ul'"""
    link_upper = link.upper()
    if link_upper == "DOWNLINK":
        return "dl"
    elif link_upper == "UPLINK":
        return "ul"
    return link.lower()

def generate_inputs():
    """Generates YAML parameter files"""
    # Use shorter prefixes to avoid Windows path length issues
    OUTPUT_START_NAME = f"out_{CAMPAIGN_NAME}_"
    PARAMETER_START_NAME = f"param_{CAMPAIGN_NAME}_"

    print(f"Generating files in: {INPUTS_DIR}")
    factory = ParametersFactory()
    clutter_types = _validate_clutter_types(CLUTTER_TYPES)
    
    total = 0  # Initialize counter

    # Campaign parameters
    Ro = 1600
    R_values = [Ro + 1000, Ro + 2000, Ro + 5000, Ro + 10000]
    load_probabilities = [50]
    p_modes = ["RANDOM_CENARIO"]
    
    # Earth Station position parameters
    use_fixed_options = [True, False]  # Iterate between FIXED and UNIFORM_DIST
    x_positions = [1, -1]  # Multipliers: 1 for x=R, -1 for x=-R
    heights = [1]  # Heights in meters

    for imt_link in ["DOWNLINK"]:
        general["imt_link"] = imt_link
        imt_link_tag = _shorten_link_tag(imt_link)  # Use shortened link tag

        for imt_id in ["imt.7300MHz.macrocell"]:
            for mss_id in ["mss.7300MHz.hubType-18"]:
                for R, load_pct, p_mode, clutter_type, use_fixed, x_mult, height in product(
                    R_values, load_probabilities, p_modes, clutter_types, use_fixed_options, x_positions, heights
                ):
                    x_pos = x_mult * R
                    location_type = "FIXED" if use_fixed else "UNIFORM"
                    print(f"Generating: {imt_link} {imt_id}→{mss_id}, R={R}, {location_type}, x={x_pos}, h={height}m, load={load_pct}%, p={p_mode}, clutter={clutter_type}")
                    total += 1

                    # Build parameters object
                    params = (
                        factory
                        .load_from_id(imt_id)
                        .load_from_id(mss_id)
                        .load_from_dict({"general": general})
                        .build()
                    )

                    # Configure scenario
                    params.general.enable_adjacent_channel = False
                    params.general.enable_cochannel = True
                    params.imt.interfered_with = False
                    params.imt.imt_dl_intra_sinr_calculation_disabled = True
                    params.single_earth_station.geometry.height = height

                    # Earth Station Position
                    if use_fixed:
                        # Use FIXED position
                        params.single_earth_station.geometry.location.type = "FIXED"
                        params.single_earth_station.geometry.location.fixed.x = x_pos
                        params.single_earth_station.geometry.location.fixed.y = 0
                       
                        
                        # UNIFORM_DIST must be disabled when using FIXED
                        # params.single_earth_station.geometry.location.type = "UNIFORM_DIST"
                        # params.single_earth_station.geometry.location.uniform_dist.min_dist_to_center = R
                        # params.single_earth_station.geometry.location.uniform_dist.max_dist_to_center = R
                    else:
                        # Use UNIFORM_DIST position
                        # params.single_earth_station.geometry.location.type = "FIXED"
                        # params.single_earth_station.geometry.location.fixed.x = x_pos
                        # params.single_earth_station.geometry.location.fixed.y = 0
                
                        
                        params.single_earth_station.geometry.location.type = "UNIFORM_DIST"
                        params.single_earth_station.geometry.location.uniform_dist.min_dist_to_center = R
                        params.single_earth_station.geometry.location.uniform_dist.max_dist_to_center = R

                    # Cluster azimuth
                    params.single_earth_station.geometry.azimuth.type = "POINTING_AT_IMT_CENTER"

                    # BS load
                    params.imt.bs.load_probability = load_pct / 100.0

                    # Configure P.452 parameters
                    p_tag = _p_mode_tag(p_mode)
                    params.single_earth_station.param_p452.percentage_p = p_mode
                    params.single_earth_station.param_p452.clutter_loss = True
                    params.single_earth_station.param_p452.clutter_type = clutter_type
                    params.single_earth_station.param_p452.Hre = height

                    # Generate file name - use shortened IDs to avoid Windows path length issues
                    imt_short = _shorten_imt_id(imt_id)
                    mss_short = _shorten_mss_id(mss_id)  # Returns empty string
                    
                    # Build filename parts - include position info
                    filename_parts = [imt_link_tag, imt_short]
                    if mss_short:  # Only add if not empty
                        filename_parts.append(mss_short)
                    
                    if use_fixed:
                        # Add position info: x position and height
                        x_tag = f"x{x_pos}" if x_pos >= 0 else f"xneg{abs(x_pos)}"
                        filename_parts.extend([f"R{R}", x_tag, f"h{height}", f"l{load_pct}", f"p-{p_tag}", f"clt-{clutter_type}"])
                    else:
                        # UNIFORM_DIST - add UNIFORM tag, R and height
                        filename_parts.extend([f"R{R}", "UNIFORM", f"h{height}", f"l{load_pct}", f"p-{p_tag}", f"clt-{clutter_type}"])
                    
                    specific = "_".join(filename_parts)
                    specific = _sanitize_for_filename(specific)

                    # Configure output paths
                    params.general.output_dir_prefix = OUTPUT_START_NAME + specific
                    output_path = INPUTS_DIR / f"{PARAMETER_START_NAME}{specific}.yaml"
                    
                    # Set file name in params object so simulator can find it
                    params.set_file_name(output_path)

                    # Write YAML file
                    try:
                        dump_parameters(output_path, params)
                        print(f"File generated: {output_path}")
                    except Exception as e:
                        print(f"Failed to generate {output_path}: {str(e)}")

    print(f"\nTotal files generated: {total}\n")

def clear_inputs():
    """Clears the input directory before generation"""
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Clearing directory: {INPUTS_DIR}")
    for item in INPUTS_DIR.iterdir():
        if item.is_file() and item.name.endswith(".yaml"):
            item.unlink()

if __name__ == "__main__":
    clear_inputs()
    generate_inputs()