"""
Generate protection margins table from simulation results.
Saves to CSV and prints a formatted table.

Negative margin = below protection threshold (PASS)
Positive margin = above protection threshold (FAIL)
"""

import re
import csv
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import numpy as np

from campaigns.mss_d2d_to_mss_adj_study_system_3.constants import CAMPAIGN_DIR

# Protection criteria: (threshold_dB, CCDF_probability)
PROTECTION_CRITERIA = [
    (-6.0, 0.2),   
    (-12.0, 0.001),  
]

INR_FILE = "system_inr.csv"


def parse_features_from_path(path: Path) -> Dict[str, Optional[str]]:
    """Parse features from output directory path."""
    s = str(path).lower()
    s_original = str(path)
    
    load_match = re.search(r"(\d+\.?\d*)load", s)
    load_factor = float(load_match.group(1)) if load_match else None
    
    offset_label = None
    offset_match = re.search(r"(offset_[a-z0-9]+mhz)", s)
    if offset_match:
        offset_label = offset_match.group(1).replace("mhz", "MHz")
    
    es_type = None
    if "7.1.4-forward-r" in s:
        es_type = "7.1.4-forward-R"
    elif "7.1.5-es-type-1" in s:
        es_type = "7.1.5-ES-type-1"
    elif "7.1.5-es-type-2" in s:
        es_type = "7.1.5-ES-type-2"
    
    sat_distance = None
    if "525km" in s:
        sat_distance = "525km"
    elif "340km" in s:
        sat_distance = "340km"
    
    exec_match = re.search(r"_(\d{4}-\d{2}-\d{2})_(\d+)$", s_original)
    execution_num = int(exec_match.group(2)) if exec_match else None
    
    if exec_match:
        base_name = s_original[:exec_match.start()]
    else:
        base_name = s_original
    
    return {
        "load_factor": load_factor,
        "offset_label": offset_label,
        "es_type": es_type,
        "sat_distance": sat_distance,
        "execution_num": execution_num,
        "base_name": base_name
    }


def load_inr_from_csv(csv_path: Path) -> np.ndarray:
    """Load INR values from CSV file."""
    try:
        data = np.loadtxt(csv_path, delimiter=',', dtype=float, skiprows=1)
        data = data.flatten()
        data = data[np.isfinite(data)]
        return data
    except Exception as e:
        print(f"Warning: Could not load {csv_path}: {e}")
        return np.array([], dtype=float)


def ecdf_to_ccdf(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Convert empirical data to CCDF."""
    if x.size == 0:
        return np.array([]), np.array([])
    xs = np.sort(x)
    cdf = np.arange(1, xs.size + 1, dtype=float) / float(xs.size)
    ccdf = np.maximum(1.0 - cdf, 1e-4)
    return xs, ccdf


def calculate_protection_margin(
    xs: np.ndarray,
    ccdf: np.ndarray,
    threshold_db: float,
    target_prob: float
) -> Optional[float]:
    """Calculate protection margin at target probability."""
    if xs.size == 0 or ccdf.size == 0:
        return None
    
    if target_prob < ccdf.min() or target_prob > ccdf.max():
        return None
    
    below_mask = ccdf <= target_prob
    above_mask = ccdf >= target_prob
    
    if not np.any(below_mask) or not np.any(above_mask):
        idx = np.argmin(np.abs(ccdf - target_prob))
        x_at_prob = xs[idx]
    else:
        above_indices = np.where(above_mask)[0]
        below_indices = np.where(below_mask)[0]
        
        if len(above_indices) > 0 and len(below_indices) > 0:
            last_above_idx = above_indices[-1]
            first_below_idx = below_indices[0]
            
            if first_below_idx == last_above_idx + 1:
                y1, y2 = ccdf[last_above_idx], ccdf[first_below_idx]
                x1, x2 = xs[last_above_idx], xs[first_below_idx]
                
                if y1 != y2:
                    x_at_prob = x1 + (x2 - x1) * (target_prob - y1) / (y2 - y1)
                else:
                    x_at_prob = (x1 + x2) / 2
            else:
                idx = np.argmin(np.abs(ccdf - target_prob))
                x_at_prob = xs[idx]
        else:
            idx = np.argmin(np.abs(ccdf - target_prob))
            x_at_prob = xs[idx]
    
    margin_db = x_at_prob - threshold_db
    return margin_db


def main():
    """Main function to generate protection margins table."""
    output_dir = CAMPAIGN_DIR / "output"
    inr_files = list(output_dir.rglob(INR_FILE))
    
    if not inr_files:
        print(f"No INR files found in {output_dir}")
        return
    
    print(f"Found {len(inr_files)} INR files")
    
    # Collect results
    results = []
    
    for csv_path in sorted(inr_files):
        output_folder = csv_path.parent
        features = parse_features_from_path(output_folder)
        
        inr_data = load_inr_from_csv(csv_path)
        if inr_data.size == 0:
            continue
        
        xs, ccdf = ecdf_to_ccdf(inr_data)
        
        # Create readable labels
        es_readable = {
            "7.1.4-forward-R": "System R",
            "7.1.5-ES-type-1": "ES Type-1",
            "7.1.5-ES-type-2": "ES Type-2",
        }
        
        offset_readable = {
            "offset_0MHz": "Nominal (2162.5 MHz)",
            "offset_minus5MHz": "-5 MHz (2157.5 MHz)",
            "offset_minus10MHz": "-10 MHz (2152.5 MHz)",
            "offset_minus15MHz": "-15 MHz (2142.5 MHz)",
        }
        
        es_name = es_readable.get(features["es_type"], features["es_type"])
        offset_name = offset_readable.get(features["offset_label"], features["offset_label"])
        sat_name = features["sat_distance"]
        
        # Calculate margins for each protection criterion
        for thr_db, prob in PROTECTION_CRITERIA:
            margin = calculate_protection_margin(xs, ccdf, thr_db, prob)
            
            if margin is not None:
                # Determine status
                if margin < 0:
                    status = "✓ PASS"
                else:
                    status = "✗ FAIL"
                
                results.append({
                    "ES_Type": es_name,
                    "Satellite_Distance": sat_name,
                    "Load_Factor": features["load_factor"],
                    "Frequency_Offset": offset_name,
                    "Protection_Threshold": f"{thr_db:.1f} dB @ {prob*100:.2f}%",
                    "Margin_dB": f"{margin:.2f}",
                    "Status": status,
                })
    
    if not results:
        print("No results found")
        return
    
    # Sort results
    results_sorted = sorted(
        results,
        key=lambda x: (
            x["ES_Type"],
            x["Satellite_Distance"],
            x["Load_Factor"] if x["Load_Factor"] is not None else float('inf'),
            x["Frequency_Offset"],
        )
    )
    
    # Save to CSV
    csv_file = CAMPAIGN_DIR / "protection_margins.csv"
    with open(csv_file, 'w', newline='') as f:
        fieldnames = ["ES_Type", "Satellite_Distance", "Load_Factor", "Frequency_Offset", 
                     "Protection_Threshold", "Margin_dB", "Status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_sorted)
    
    print(f"\n✓ CSV saved to: {csv_file}\n")
    
    # Print formatted table
    print("=" * 140)
    print("PROTECTION MARGINS TABLE - Negative = PASS (below threshold), Positive = FAIL (above threshold)")
    print("=" * 140)
    print(f"{'ES Type':<15} {'Satellite':<12} {'Load':<8} {'Frequency Offset':<25} {'Threshold':<20} {'Margin (dB)':<15} {'Status':<10}")
    print("-" * 140)
    
    for row in results_sorted:
        load_display = f"{row['Load_Factor']:.2f}" if row['Load_Factor'] is not None else "N/A"
        print(f"{row['ES_Type']:<15} {row['Satellite_Distance']:<12} {load_display:<8} {row['Frequency_Offset']:<25} "
              f"{row['Protection_Threshold']:<20} {row['Margin_dB']:>14} {row['Status']:>9}")
    
    print("=" * 140)
    
    # Summary statistics
    passed = sum(1 for r in results_sorted if "PASS" in r["Status"])
    failed = sum(1 for r in results_sorted if "FAIL" in r["Status"])
    
    print(f"\nSUMMARY:")
    print(f"  Total scenarios: {len(results_sorted)}")
    print(f"  Passed (margin < 0): {passed}")
    print(f"  Failed (margin > 0): {failed}")
    print(f"  Pass rate: {100*passed/len(results_sorted):.1f}%")


if __name__ == "__main__":
    main()
