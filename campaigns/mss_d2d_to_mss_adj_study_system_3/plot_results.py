"""Plot CCDF of INR results from mss_d2d_to_mss_study campaign."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from campaigns.mss_d2d_to_mss_adj_study_system_3.constants import CAMPAIGN_DIR

# ===================== USER SETTINGS =====================
# Protection criteria: (threshold_dB, CCDF_probability)
PROTECTION_CRITERIA: List[Tuple[float, float]] = [
    (-12.0, 0.001),   # -12 dB at 0.1%
    (-6.0, 0.2),      # -6 dB at 20%

]

# Plot appearance
TITLE_PREFIX = "CCDF of INR - MSS D2D to MSS Study"
XLABEL = "INR [dB]"
YLABEL = "P(X > x)"
CCDF_FLOOR = 1e-4
FIGSIZE = (12, 8)

# File to search
INR_FILE = "system_inr.csv"

# Which curves to plot - configure here
# Format: (load_factor, offset_label, es_type, sat_distance, custom_label)
#   - load_factor: 0.1, 0.2, 0.5 or None for all
#   - offset_label: "offset_0MHz", "offset_minus5MHz", "offset_minus10MHz", "offset_minus15MHz", or None for all
#   - es_type: "7.1.4-forward-R", "7.1.5-ES-type-1", "7.1.5-ES-type-2" or None for all
#   - sat_distance: "525km", "340km" or None for all
#   - custom_label: Custom name for this curve (optional, None uses auto-generated label)
CURVES_TO_PLOT = [
    # Examples (uncomment to use):
    # (0.1, "offset_0MHz", "7.1.5-ES-type-1", "525km", "ES Type-1 @ 525km - Nominal"),
    # (0.1, None, "7.1.5-ES-type-1", "525km", None),  # All offsets
]

# If CURVES_TO_PLOT is empty, plot all curves
PLOT_ALL_IF_EMPTY = True

# How to handle duplicate simulations (same parameters, different execution numbers)
# Options:
#   - "latest": Use only the most recent execution (highest number)
#   - "all": Plot all executions as separate curves
#   - int: Use only execution with this specific number (e.g., 1 for _01, 2 for _02)
DUPLICATE_HANDLING = "latest"
# =========================================================



def parse_features_from_path(path: Path) -> Dict[str, Optional[str]]:
    """Parse features from output directory path for mss_d2d_to_mss_adj_study."""
    s = str(path).lower()
    s_original = str(path)
    
    # Extract load factor (e.g., 0.1load, 0.2load, 0.5load)
    load_match = re.search(r"(\d+\.?\d*)load", s)
    load_factor = float(load_match.group(1)) if load_match else None
    
    # Extract offset label (e.g., offset_0mhz, offset_minus5mhz, offset_minus10mhz, offset_minus15mhz)
    # Pattern matches: offset_<anything>mhz (including minus and digits)
    offset_label = None
    offset_match = re.search(r"(offset_[a-z0-9]+mhz)", s)
    if offset_match:
        # Convert back to standard format with MHz capitalized
        offset_label = offset_match.group(1).replace("mhz", "MHz")
    
    # Extract ES type
    es_type = None
    if "7.1.4-forward-r" in s:
        es_type = "7.1.4-forward-R"
    elif "7.1.5-es-type-1" in s:
        es_type = "7.1.5-ES-type-1"
    elif "7.1.5-es-type-2" in s:
        es_type = "7.1.5-ES-type-2"
    
    # Extract satellite distance
    sat_distance = None
    if "525km" in s:
        sat_distance = "525km"
    elif "340km" in s:
        sat_distance = "340km"
    
    # Extract execution number (e.g., _01, _02 from end of folder name)
    exec_match = re.search(r"_(\d{4}-\d{2}-\d{2})_(\d+)$", s_original)
    execution_num = int(exec_match.group(2)) if exec_match else None
    
    # Extract base name (without execution number) for grouping duplicates
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
        # Skip first row (header)
        data = np.loadtxt(csv_path, delimiter=',', dtype=float, skiprows=1)
        # Flatten if needed
        data = data.flatten()
        # Remove NaN and infinite values
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
    ccdf = np.maximum(1.0 - cdf, CCDF_FLOOR)
    return xs, ccdf


def matches_filter(features: Dict, filter_tuple: Tuple) -> bool:
    """Check if features match the filter tuple.
    Format: (load_factor, offset_label, es_type, sat_distance, custom_label)
    """
    if len(filter_tuple) < 4:
        return False
    
    load_filt = filter_tuple[0]
    offset_filt = filter_tuple[1]
    es_filt = filter_tuple[2]
    sat_filt = filter_tuple[3]
    
    if load_filt is not None and features.get("load_factor") != load_filt:
        return False
    if offset_filt is not None and features.get("offset_label") != offset_filt:
        return False
    if es_filt is not None and features.get("es_type") != es_filt:
        return False
    if sat_filt is not None and features.get("sat_distance") != sat_filt:
        return False
    
    return True


def create_label(features: Dict) -> str:
    """Create label for curve based on features."""
    parts = []
    
    es_readable = {
        "7.1.4-forward-R": "System R",
        "7.1.5-ES-type-1": "ES Type-1",
        "7.1.5-ES-type-2": "ES Type-2",
    }
    
    offset_readable = {
        "offset_0MHz": "Nominal",
        "offset_minus5MHz": "-5 MHz",
        "offset_minus10MHz": "-10 MHz",
        "offset_minus15MHz": "-15 MHz",
    }
    
    if features.get("es_type"):
        parts.append(es_readable.get(features["es_type"], features["es_type"]))
    
    if features.get("sat_distance"):
        parts.append(f"{features['sat_distance']}")
    
    if features.get("offset_label"):
        parts.append(offset_readable.get(features["offset_label"], features["offset_label"]))
    
    if features.get("load_factor"):
        parts.append(f"Load {features['load_factor']*100:.0f}%")
    
    return " / ".join(parts)


def calculate_protection_margin(
    xs: np.ndarray,
    ccdf: np.ndarray,
    threshold_db: float,
    target_prob: float
) -> Optional[float]:
    """
    Calculate how many dB a curve is from a protection criterion.
    
    Returns the difference: curve_value_at_prob - threshold_db
    Positive value means curve is above threshold (worse),
    negative means below threshold (better).
    """
    if xs.size == 0 or ccdf.size == 0:
        return None
    
    # Check if target_prob is within range
    if target_prob < ccdf.min() or target_prob > ccdf.max():
        return None
    
    # Find where CCDF crosses target_prob
    below_mask = ccdf <= target_prob
    above_mask = ccdf >= target_prob
    
    if not np.any(below_mask) or not np.any(above_mask):
        # Find closest value
        idx = np.argmin(np.abs(ccdf - target_prob))
        x_at_prob = xs[idx]
    else:
        # Find transition point
        above_indices = np.where(above_mask)[0]
        below_indices = np.where(below_mask)[0]
        
        if len(above_indices) > 0 and len(below_indices) > 0:
            last_above_idx = above_indices[-1]
            first_below_idx = below_indices[0]
            
            # Linear interpolation if adjacent
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
    
    # Calculate margin: difference from threshold
    margin_db = x_at_prob - threshold_db
    
    return margin_db


def print_protection_margins_table(
    curves_data: List[Dict],
    protection_criteria: List[Tuple[float, float]]
):
    """Print a table showing how many dB each curve is from protection criteria."""
    if not protection_criteria or not curves_data:
        return
    
    print("\n" + "="*100)
    print("PROTECTION MARGINS TABLE")
    print("="*100)
    print("Values show: curve_INR_at_probability - criterion_threshold (dB)")
    print("Positive = above threshold (worse), Negative = below threshold (better)")
    print("="*100)
    
    # Calculate margins for each curve and criterion
    margins = []
    curve_labels = []
    criterion_labels = []
    
    for curve in curves_data:
        xs, ccdf = ecdf_to_ccdf(curve["data"])
        if xs.size == 0:
            continue
        
        curve_labels.append(curve["label"])
        curve_margins = []
        
        for thr_db, prob in protection_criteria:
            criterion_label = f"{thr_db:.1f} dB @ {prob*100:.2f}%"
            if criterion_label not in criterion_labels:
                criterion_labels.append(criterion_label)
            
            margin = calculate_protection_margin(xs, ccdf, thr_db, prob)
            curve_margins.append(margin)
        
        margins.append(curve_margins)
    
    if not margins:
        print("No data available for margin calculation")
        return
    
    # Print header
    header = f"{'Curve':<50}"
    for crit_label in criterion_labels:
        header += f"{crit_label:>20}"
    print(header)
    print("-" * (50 + 20 * len(criterion_labels)))
    
    # Print rows
    for i, (label, curve_margins) in enumerate(zip(curve_labels, margins)):
        row = f"{label:<50}"
        for margin in curve_margins:
            if margin is not None:
                row += f"{margin:>20.2f}"
            else:
                row += f"{'N/A':>20}"
        print(row)
    
    print("="*100 + "\n")


def filter_duplicate_simulations(
    inr_files: List[Path],
    duplicate_handling: str = "latest"
) -> List[Path]:
    """Filter duplicate simulations based on duplicate_handling strategy."""
    if duplicate_handling == "all":
        return inr_files
    
    # Group files by base name (same simulation, different executions)
    grouped = {}
    for csv_path in inr_files:
        output_folder = csv_path.parent
        features = parse_features_from_path(output_folder)
        base_name = features.get("base_name")
        exec_num = features.get("execution_num")
        
        if base_name:
            if base_name not in grouped:
                grouped[base_name] = []
            grouped[base_name].append((exec_num, csv_path))
    
    # Filter based on strategy
    filtered_files = []
    for base_name, files in grouped.items():
        if len(files) == 1:
            # No duplicates, keep it
            filtered_files.append(files[0][1])
        else:
            # Has duplicates, apply strategy
            if duplicate_handling == "latest":
                # Keep the one with highest execution number
                files.sort(
                    key=lambda x: x[0] if x[0] is not None else -1,
                    reverse=True
                )
                filtered_files.append(files[0][1])
            elif isinstance(duplicate_handling, int):
                # Keep only the one with specific execution number
                matching = [f for f in files if f[0] == duplicate_handling]
                if matching:
                    filtered_files.append(matching[0][1])
                else:
                    # If not found, keep the latest
                    files.sort(
                        key=lambda x: x[0] if x[0] is not None else -1,
                        reverse=True
                    )
                    filtered_files.append(files[0][1])
            else:
                # Unknown strategy, keep all
                filtered_files.extend([f[1] for f in files])
    
    return filtered_files


def plot_ccdf_inr(
    curves_to_plot: Optional[List[Tuple]] = None,
    legend_loc: str = "best",
    legend_fontsize: float = 10,
    legend_ncol: int = 1,
    legend_framealpha: float = 0.95,
    show_protection_criteria: bool = True,
    protection_criteria: Optional[List[Tuple[float, float]]] = None,
    duplicate_handling: Optional[Union[str, int]] = None
):
    """Main plotting function for INR CCDF."""
    if curves_to_plot is None:
        curves_to_plot = CURVES_TO_PLOT if CURVES_TO_PLOT else []
    
    if protection_criteria is None:
        protection_criteria = PROTECTION_CRITERIA
    
    if duplicate_handling is None:
        duplicate_handling = DUPLICATE_HANDLING
    
    # Find all INR CSV files
    output_dir = CAMPAIGN_DIR / "output"
    inr_files = list(output_dir.rglob(INR_FILE))
    
    if not inr_files:
        print(f"No INR files found in {output_dir}")
        return
    
    print(f"Found {len(inr_files)} INR files")
    
    # Filter duplicate simulations
    inr_files = filter_duplicate_simulations(inr_files, duplicate_handling)
    print(
        f"After filtering duplicates ({duplicate_handling}): "
        f"{len(inr_files)} files"
    )
    
    # Load and organize data
    curves_data = []
    for csv_path in inr_files:
        output_folder = csv_path.parent
        features = parse_features_from_path(output_folder)
        
        # Check if this curve should be plotted
        if curves_to_plot:
            matched = False
            matched_filter = None
            for filt in curves_to_plot:
                if matches_filter(features, filt):
                    matched = True
                    matched_filter = filt
                    break
            
            if not matched:
                continue
        else:
            matched_filter = None
        
        # Load INR data
        inr_data = load_inr_from_csv(csv_path)
        if inr_data.size == 0:
            continue
        
        # Determine label
        if matched_filter and len(matched_filter) >= 5 and matched_filter[4]:
            # Use custom label from filter tuple (5th element, index 4)
            label = matched_filter[4]
        else:
            label = create_label(features)
        
        curves_data.append({
            "features": features,
            "data": inr_data,
            "label": label,
            "path": output_folder
        })
    
    if not curves_data:
        print("No curves to plot after filtering")
        return
    
    print(f"Plotting {len(curves_data)} curves")
    
    # Calculate and print protection margins table
    if show_protection_criteria and protection_criteria:
        print_protection_margins_table(curves_data, protection_criteria)
    
    # Sort curves for consistent color ordering
    def get_sort_key(features: Dict) -> Tuple:
        """Sort by ES type, then satellite distance, then offset, then load."""
        es_order = {
            "7.1.4-forward-R": 0,
            "7.1.5-ES-type-1": 1,
            "7.1.5-ES-type-2": 2,
        }
        sat_order = {"525km": 0, "340km": 1}
        offset_order = {
            "offset_0MHz": 0,
            "offset_minus5MHz": 1,
            "offset_minus10MHz": 2,
            "offset_minus15MHz": 3,
        }
        
        return (
            es_order.get(features.get("es_type"), 99),
            sat_order.get(features.get("sat_distance"), 99),
            offset_order.get(features.get("offset_label"), 99),
            features.get("load_factor") or 0,
        )
    
    curves_data_sorted = sorted(
        curves_data,
        key=lambda c: get_sort_key(c["features"])
    )
    
    # Create plot
    fig, ax = plt.subplots(figsize=FIGSIZE)
    
    # Plot each curve
    for curve in curves_data_sorted:
        xs, ccdf = ecdf_to_ccdf(curve["data"])
        if xs.size > 0:
            ax.semilogy(
                xs, ccdf,
                drawstyle="steps-post",
                label=curve["label"],
                linewidth=1.8
            )
    
    # Add protection criteria lines
    pc_handles = []
    if show_protection_criteria and protection_criteria:
        # Protection criteria styles
        PROTECTION_STYLES = [
            dict(color="#d62728", linestyle="--", linewidth=2.0),  # Red
            dict(color="#ff7f0e", linestyle="--", linewidth=2.0),  # Orange
            dict(color="#5c1919", linestyle=":", linewidth=2.2),   # Brown
        ]
        
        for idx, (thr_db, prob) in enumerate(protection_criteria):
            st = PROTECTION_STYLES[idx % len(PROTECTION_STYLES)]
            
            # Vertical line at threshold
            ax.axvline(thr_db, alpha=0.85, zorder=3, **st)
            # Horizontal line at probability
            ax.axhline(prob, alpha=0.85, zorder=3, **st)
            
            # Legend entry
            pc_handles.append(Line2D(
                [], [],
                color=st["color"],
                linestyle=st["linestyle"],
                linewidth=st["linewidth"],
                label=f"Protection: {thr_db:.1f} dB @ {prob*100:.3g}%"
            ))
    
    # Configure plot
    ax.set_title(TITLE_PREFIX, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(XLABEL, fontsize=12, fontweight='bold')
    ax.set_ylabel(YLABEL, fontsize=12, fontweight='bold')
    ax.set_ylim(CCDF_FLOOR, 1.0)
    ax.grid(True, which="both", alpha=0.3, linestyle=':')
    
    # Combine legends
    handles, labels = ax.get_legend_handles_labels()
    handles.extend(pc_handles)
    
    # Handle legend location
    if legend_loc.lower() == "outside":
        ax.legend(
            handles=handles,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            fontsize=legend_fontsize,
            ncol=legend_ncol,
            framealpha=legend_framealpha
        )
    else:
        ax.legend(
            handles=handles,
            loc=legend_loc,
            fontsize=legend_fontsize,
            ncol=legend_ncol,
            framealpha=legend_framealpha
        )
    
    # Save figure
    plots_dir = CAMPAIGN_DIR / "plot"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = plots_dir / "ccdf_inr.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[SUCCESS] Plot saved to: {output_file}")
    
    # Also save as PDF
    output_file_pdf = plots_dir / "ccdf_inr.pdf"
    plt.savefig(output_file_pdf, dpi=300, bbox_inches='tight')
    print(f"[SUCCESS] Plot saved to: {output_file_pdf}")
    
    plt.show()


if __name__ == "__main__":
    # ===================== MAIN CONFIGURATION =====================
    # Configure which curves to plot
    # Format: (load_factor, offset_label, es_type, sat_distance, custom_label)
    # offset_label options: "offset_0MHz", "offset_minus5MHz", "offset_minus10MHz", "offset_minus15MHz"
    
    curves_to_plot = [
        # ========== System R (7.1.4-forward-R) ==========
        # @ 525 km
        #(0.1, "offset_0MHz", "7.1.4-forward-R", "525km", "System R @ 525km - Nominal (2162.5 MHz)"),
        #(0.1, "offset_minus5MHz", "7.1.4-forward-R", "525km", "System R @ 525km - (2157.5 MHz)"),
        #(0.1, "offset_minus10MHz", "7.1.4-forward-R", "525km", "System R @ 525km - (2152.5 MHz)"),
        #(0.1, "offset_minus15MHz", "7.1.4-forward-R", "525km", "System R @ 525km - (2142.5 MHz)"),
        
        # @ 340 km
        #(0.1, "offset_0MHz", "7.1.4-forward-R", "340km", "System R @ 340km - Nominal (2162.5 MHz)"),
        #(0.1, "offset_minus5MHz", "7.1.4-forward-R", "340km", "System R @ 340km - (2157.5 MHz)"),
        #(0.1, "offset_minus10MHz", "7.1.4-forward-R", "340km", "System R @ 340km - (2152.5 MHz)"),
        #(0.1, "offset_minus15MHz", "7.1.4-forward-R", "340km", "System R @ 340km - (2142.5 MHz)"),
        
        # ========== ES Type-1 (7.1.5-ES-type-1) ==========
        # @ 525 km
        #(0.1, "offset_0MHz", "7.1.5-ES-type-1", "525km", "ES Type-1 @ 525km - Nominal (2162.5 MHz)"),
        #(0.1, "offset_minus5MHz", "7.1.5-ES-type-1", "525km", "ES Type-1 @ 525km - (2157.5 MHz)"),
        #(0.1, "offset_minus10MHz", "7.1.5-ES-type-1", "525km", "ES Type-1 @ 525km - (2152.5 MHz)"),
        #(0.1, "offset_minus15MHz", "7.1.5-ES-type-1", "525km", "ES Type-1 @ 525km - (2142.5 MHz)"),
        
        # @ 340 km
        #(0.1, "offset_0MHz", "7.1.5-ES-type-1", "340km", "ES Type-1 @ 340km - Nominal (2162.5 MHz)"),
        #(0.1, "offset_minus5MHz", "7.1.5-ES-type-1", "340km", "ES Type-1 @ 340km - (2157.5 MHz)"),
        #(0.1, "offset_minus10MHz", "7.1.5-ES-type-1", "340km", "ES Type-1 @ 340km - (2152.5 MHz)"),
        #(0.1, "offset_minus15MHz", "7.1.5-ES-type-1", "340km", "ES Type-1 @ 340km - (2142.5 MHz)"),
        
        # ========== ES Type-2 (7.1.5-ES-type-2) ==========
        # @ 525 km
        #(0.1, "offset_0MHz", "7.1.5-ES-type-2", "525km", "ES Type-2 @ 525km - Nominal (2162.5 MHz)"),
        (0.1, "offset_minus5MHz", "7.1.5-ES-type-2", "525km", "ES Type-2 @ 525km - (-5 MHz, 2157.5 MHz)"),
        (0.1, "offset_minus10MHz", "7.1.5-ES-type-2", "525km", "ES Type-2 @ 525km - (-10 MHz, 2152.5 MHz)"),
        (0.1, "offset_minus15MHz", "7.1.5-ES-type-2", "525km", "ES Type-2 @ 525km - (-15 MHz, 2142.5 MHz)"),
        
        # @ 340 km
        #(0.1, "offset_0MHz", "7.1.5-ES-type-2", "340km", "ES Type-2 @ 340km - Nominal (2162.5 MHz)"),
        (0.1, "offset_minus5MHz", "7.1.5-ES-type-2", "340km", "ES Type-2 @ 340km - (-5 MHz, 2157.5 MHz)"),
        (0.1, "offset_minus10MHz", "7.1.5-ES-type-2", "340km", "ES Type-2 @ 340km - (-10 MHz, 2152.5 MHz)"),
        (0.1, "offset_minus15MHz", "7.1.5-ES-type-2", "340km", "ES Type-2 @ 340km - (-15 MHz, 2142.5 MHz)"),
    ]
    # Legend configuration
    legend_location = "best"
    legend_font_size = 10
    legend_columns = 1
    legend_alpha = 0.95
    
    # Protection criteria
    show_protection = True
    protection_criteria = [
        (-12.0, 0.001),
        (-6.0, 0.2),
    ]
    
    # Duplicate handling
    duplicate_handling = "latest"
    # =========================================================
    
    plot_ccdf_inr(
        curves_to_plot=curves_to_plot if curves_to_plot else None,
        legend_loc=legend_location,
        legend_fontsize=legend_font_size,
        legend_ncol=legend_columns,
        legend_framealpha=legend_alpha,
        show_protection_criteria=show_protection,
        protection_criteria=protection_criteria,
        duplicate_handling=duplicate_handling
    )