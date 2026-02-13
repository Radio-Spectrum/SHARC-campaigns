"""
Generate a CSV table with protection margins for selected simulations.

This script calculates protection margins (dB differences from criteria) for
simulations filtered by distance and clutter type, then prints and saves to CSV.
"""

from __future__ import annotations

import sys
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

# Add project root so "campaigns" is importable when script is run directly
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Add SHARC simulator so "import sharc" works (layout: sharc_simulator/SHARC/sharc)
_sharc_root = _project_root.parent / "SHARC"
if _sharc_root.exists() and str(_sharc_root) not in sys.path:
    sys.path.insert(0, str(_sharc_root))

# Import functions from plot_ccdf_inr.py (same directory)
from plot_ccdf_inr import (
    OUTPUT_DIR,
    INR_FILE,
    PROTECTION_CRITERIA,
    parse_features_from_path,
    load_inr_from_csv,
    ecdf_to_ccdf,
    calculate_protection_margin,
    filter_duplicate_simulations,
    create_label,
)

# ===================== CONFIGURATION =====================
# Distances to include (in meters, from center)
# These will be matched against R values in simulation folders
#distance = [30000, 35000, 40000, 45000, 50000]
distance = [230000, 235000, 240000, 245000, 250000]
DISTANCES = [1600 + d for d in distance]  # Example: [230000, 235000, ...]

# Clutter type to filter: "one_end", "both_ends", or None for all
CLUTTER_TYPE = "one_end"  # Options: "one_end", "both_ends", or None

# Location type: "direita" (x>0), "esquerda" (x<0), "uniforme", or None
LOCATION_TYPE = None  # Options: "direita", "esquerda", "uniforme", or None

# Height to filter (in meters): specific value or None for all
HEIGHT = None  # Options: 5, 40, or None for all

# How to handle duplicate simulations (always use latest)
DUPLICATE_HANDLING_CONFIG = "latest"  # Always uses most recent simulation

# Output CSV filename
OUTPUT_CSV = "protection_margins.csv"
# =========================================================


def _get_location_category(features: Dict) -> str:
    """
    Determine location category: "direita", "esquerda", or "uniforme".
    
    Parameters
    ----------
    features : Dict
        Features dictionary from parse_features_from_path
    
    Returns
    -------
    str
        "direita" (x > 0), "esquerda" (x < 0), or "uniforme" (UNIFORM)
    """
    if features["location_type"] == "UNIFORM":
        return "uniforme"
    elif features["location_type"] == "FIXED":
        if features["x"] is not None:
            if features["x"] > 0:
                return "direita"
            elif features["x"] < 0:
                return "esquerda"
    return "unknown"


def generate_margins_table(
    distances: Optional[List[int]] = None,
    clutter_type: Optional[str] = None,
    location_type: Optional[str] = None,
    height: Optional[int] = None,
    duplicate_handling: Union[str, int] = "latest",
    protection_criteria: Optional[List[Tuple[float, float]]] = None,
    output_csv: Optional[str] = None,
) -> List[Dict]:
    """
    Generate protection margins table for filtered simulations.
    
    Parameters
    ----------
    distances : Optional[List[int]]
        List of R values (distances) to include. None for all.
    clutter_type : Optional[str]
        Clutter type to filter: "one_end", "both_ends", or None for all.
    location_type : Optional[str]
        Location type: "direita" (x>0), "esquerda" (x<0),
        "uniforme" (UNIFORM), or None for all.
    height : Optional[int]
        Height to filter (in meters) or None for all.
    duplicate_handling : Union[str, int]
        How to handle duplicate simulations: "latest" (default), "all", or int.
    protection_criteria : Optional[List[Tuple[float, float]]]
        Protection criteria. If None, uses PROTECTION_CRITERIA.
    output_csv : Optional[str]
        Output CSV filename. If None, uses OUTPUT_CSV.
    
    Returns
    -------
    List[Dict]
        List of dictionaries with margin data for each simulation.
    """
    if protection_criteria is None:
        protection_criteria = PROTECTION_CRITERIA
    
    if output_csv is None:
        output_csv = OUTPUT_CSV
    
    # Always use "latest" for duplicate handling unless explicitly overridden
    if duplicate_handling is None:
        duplicate_handling = "latest"
    
    # Find all INR CSV files
    inr_files = list(OUTPUT_DIR.rglob(INR_FILE))
    
    if not inr_files:
        print(f"No INR files found in {OUTPUT_DIR}")
        return []
    
    print(f"Found {len(inr_files)} INR files")
    
    # Filter duplicate simulations (always use latest)
    inr_files = filter_duplicate_simulations(inr_files, duplicate_handling)
    print(f"After filtering duplicates ({duplicate_handling}): {len(inr_files)} files")
    
    # Filter and load data
    curves_data = []
    for csv_path in inr_files:
        output_folder = csv_path.parent
        features = parse_features_from_path(output_folder)
        
        # Determine location category
        loc_category = _get_location_category(features)
        
        # Apply filters
        if distances is not None and features["R"] not in distances:
            continue
        if clutter_type is not None and features["clutter"] != clutter_type:
            continue
        if location_type is not None and loc_category != location_type:
            continue
        if height is not None and features["height"] != height:
            continue
        
        # Load INR data
        inr_data = load_inr_from_csv(csv_path)
        if inr_data.size == 0:
            continue
        
        label = create_label(features)
        
        curves_data.append({
            "features": features,
            "data": inr_data,
            "label": label,
            "path": output_folder
        })
    
    if not curves_data:
        print("No curves found matching the filters")
        return []
    
    print(f"Processing {len(curves_data)} simulations")
    
    # Calculate margins
    table_data = []
    for curve in curves_data:
        xs, ccdf = ecdf_to_ccdf(curve["data"])
        if xs.size == 0:
            continue
        
        features = curve["features"]
        loc_category = _get_location_category(features)
        
        row = {
            "R": features["R"],
            "x": features["x"],
            "height": features["height"],
            "clutter": features["clutter"],
            "location_type": loc_category,  # Use category: "direita", "esquerda", "uniforme"
            "label": curve["label"],
        }
        
        # Calculate margin for each protection criterion
        for thr_db, prob in protection_criteria:
            criterion_key = f"{thr_db}dB_{prob*100:.2f}%"
            margin = calculate_protection_margin(xs, ccdf, thr_db, prob)
            row[criterion_key] = margin
        
        table_data.append(row)
    
    # Sort by R, location category, then height
    location_order = {
        "direita": 0, "esquerda": 1, "uniforme": 2, "unknown": 3
    }
    table_data.sort(key=lambda x: (
        x["R"] if x["R"] is not None else 0,
        location_order.get(x.get("location_type", "unknown"), 3),
        x["height"] if x["height"] is not None else 0,
    ))
    
    return table_data


def print_margins_table(table_data: List[Dict], protection_criteria: List[Tuple[float, float]]):
    """Print formatted margins table to console."""
    if not table_data:
        print("No data to display")
        return
    
    print("\n" + "="*100)
    print("PROTECTION MARGINS TABLE")
    print("="*100)
    print("Values show: curve_INR_at_probability - criterion_threshold (dB)")
    print("Positive = above threshold (worse), Negative = below threshold (better)")
    print("="*100)
    
    # Build header
    criterion_labels = []
    for thr_db, prob in protection_criteria:
        label = f"{thr_db} dB @ {prob*100:.2f}%"
        criterion_labels.append(label)
    
    # Print header
    header = f"{'R':<10} {'Location':<12} {'Height':<8} {'Clutter':<12} {'Label':<40}"
    for crit_label in criterion_labels:
        header += f"{crit_label:>20}"
    print(header)
    print("-" * (10 + 12 + 8 + 12 + 40 + 20 * len(criterion_labels)))
    
    # Print rows
    for row in table_data:
        r_str = str(row["R"]) if row["R"] is not None else "N/A"
        # Already categorized as "direita", "esquerda", "uniforme"
        loc_str = row.get("location_type", "N/A")
        h_str = f"{row['height']}m" if row["height"] is not None else "N/A"
        clt_str = row["clutter"] or "N/A"
        label_str = row["label"][:40]  # Truncate if too long
        
        line = f"{r_str:<10} {loc_str:<12} {h_str:<8} {clt_str:<12} {label_str:<40}"
        
        for thr_db, prob in protection_criteria:
            criterion_key = f"{thr_db}dB_{prob*100:.2f}%"
            margin = row.get(criterion_key)
            if margin is not None:
                line += f"{margin:>20.2f}"
            else:
                line += f"{'N/A':>20}"
        
        print(line)
    
    print("="*100 + "\n")


def save_margins_csv(
    table_data: List[Dict],
    protection_criteria: List[Tuple[float, float]],
    output_path: Path
):
    """Save margins table to CSV file."""
    if not table_data:
        print("No data to save")
        return
    
    # Build column names
    columns = ["R", "x", "height", "clutter", "location_type", "label"]
    for thr_db, prob in protection_criteria:
        columns.append(f"{thr_db}dB_{prob*100:.2f}%")
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for row in table_data:
            # Prepare row for CSV (convert None to empty string)
            csv_row = {}
            for col in columns:
                value = row.get(col)
                if value is None:
                    csv_row[col] = ""
                else:
                    csv_row[col] = value
            writer.writerow(csv_row)
    
    print(f"CSV saved to: {output_path}")


if __name__ == "__main__":
    # Use configuration from top of file
    table_data = generate_margins_table(
        distances=DISTANCES,
        clutter_type=CLUTTER_TYPE,
        location_type=LOCATION_TYPE,
        height=HEIGHT,
        duplicate_handling=DUPLICATE_HANDLING_CONFIG,
    )
    
    if table_data:
        # Print table
        print_margins_table(table_data, PROTECTION_CRITERIA)
        
        # Save CSV in campaign directory
        output_path = Path(__file__).parent / OUTPUT_CSV
        save_margins_csv(table_data, PROTECTION_CRITERIA, output_path)
    else:
        print("No data generated. Check your filters.")

