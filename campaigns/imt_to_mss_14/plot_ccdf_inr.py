from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from campaigns.imt_to_mss_14.constants import OUTPUT_DIR

# ===================== USER SETTINGS =====================
# Protection criteria: (threshold_dB, CCDF_probability)
PROTECTION_CRITERIA: List[Tuple[float, float]] = [
    (-10.5, 0.20),   # -10.5 dB at 20%
    (-7.0, 0.001),   # -7 dB at 0.1%
    (-6.0, 0.0003),  # -6 dB at 0.03%
]

# Plot appearance
TITLE_PREFIX = "CCDF of INR"
XLABEL = "INR [dB]"
YLABEL = "P(X > x)"
CCDF_FLOOR = 1e-5
FIGSIZE = (10, 7)

# File to search
INR_FILE = "system_inr.csv"

# Which curves to plot - configure here
# Format: (R, x_pos, height, clutter, location_type, custom_label)
#   - R: Distance from center in meters (e.g., 2600, 3600, 6600) or None for all
#   - x_pos: X position in meters for FIXED location (e.g., 2600, -2600) or None for all/UNIFORM
#   - height: Earth station height in meters (e.g., 5, 40) or None for all
#   - clutter: Clutter type ("one_end", "both_ends") or None for all
#   - location_type: "FIXED" or "UNIFORM" or None for all
#   - custom_label: Custom name for this curve (optional, None uses auto-generated label)
CURVES_TO_PLOT = [
    # Example: (R, x_pos, height, clutter, location_type, custom_label)
    # (2600, None, 5, "one_end", "FIXED", "R=2600, h=5m, one_end"),
    # Or leave empty to plot all curves
]

# If CURVES_TO_PLOT is empty, plot all curves
PLOT_ALL_IF_EMPTY = True
# =========================================================

def parse_features_from_path(path: Path) -> Dict[str, Optional[str]]:
    """Parse features from output directory path"""
    s = str(path).lower()
    
    # Extract R value
    r_match = re.search(r"r(\d+)", s)
    r_value = int(r_match.group(1)) if r_match else None
    
    # Extract x position
    x_match = re.search(r"x(?:neg)?(\d+)", s)
    if x_match:
        x_str = x_match.group(0)
        if "xneg" in x_str:
            x_value = -int(re.search(r"xneg(\d+)", s).group(1))
        else:
            x_value = int(re.search(r"x(\d+)", s).group(1))
    else:
        x_value = None
    
    # Extract height
    h_match = re.search(r"h(\d+)", s)
    height = int(h_match.group(1)) if h_match else None
    
    # Extract clutter type
    clutter = None
    if "clt-both_ends" in s or "clt_both_ends" in s:
        clutter = "both_ends"
    elif "clt-one_end" in s or "clt_one_end" in s:
        clutter = "one_end"
    
    # Extract location type
    location_type = None
    if "uniform" in s:
        location_type = "UNIFORM"
    elif "x" in s and x_value is not None:  # Has x position means FIXED
        location_type = "FIXED"
    
    return {
        "R": r_value,
        "x": x_value,
        "height": height,
        "clutter": clutter,
        "location_type": location_type
    }

def load_inr_from_csv(csv_path: Path) -> np.ndarray:
    """Load INR values from CSV file"""
    try:
        # Skip first row (header) - CSV files have "samples" as header
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
    """Convert empirical data to CCDF"""
    if x.size == 0:
        return np.array([]), np.array([])
    xs = np.sort(x)
    cdf = np.arange(1, xs.size + 1, dtype=float) / float(xs.size)
    ccdf = np.maximum(1.0 - cdf, CCDF_FLOOR)
    return xs, ccdf

def matches_filter(features: Dict, filter_tuple: Tuple) -> bool:
    """Check if features match the filter tuple"""
    # Handle both 5-tuple (without custom_label) and 6-tuple (with custom_label)
    if len(filter_tuple) == 6:
        r_filt, x_filt, h_filt, clt_filt, loc_filt, _ = filter_tuple
    else:
        r_filt, x_filt, h_filt, clt_filt, loc_filt = filter_tuple
    
    if r_filt is not None and features["R"] != r_filt:
        return False
    if x_filt is not None and features["x"] != x_filt:
        return False
    if h_filt is not None and features["height"] != h_filt:
        return False
    if clt_filt is not None and features["clutter"] != clt_filt:
        return False
    if loc_filt is not None and features["location_type"] != loc_filt:
        return False
    
    return True

def create_label(features: Dict) -> str:
    """Create label for curve based on features"""
    parts = []
    
    if features["R"]:
        parts.append(f"R={features['R']}")
    
    if features["location_type"] == "FIXED":
        if features["x"]:
            x_str = f"x={features['x']}" if features["x"] >= 0 else f"x={features['x']}"
            parts.append(x_str)
    elif features["location_type"] == "UNIFORM":
        parts.append("UNIFORM")
    
    if features["height"]:
        parts.append(f"h={features['height']}m")
    
    if features["clutter"]:
        parts.append(f"clt={features['clutter']}")
    
    return ", ".join(parts)

def calculate_protection_margin(xs: np.ndarray, ccdf: np.ndarray, threshold_db: float, target_prob: float) -> Optional[float]:
    """
    Calculate how many dB a curve is from a protection criterion.
    
    Returns the difference: curve_value_at_prob - threshold_db
    Positive value means curve is above threshold (worse), negative means below (better).
    """
    if xs.size == 0 or ccdf.size == 0:
        return None
    
    # Find the INR value at the target probability using interpolation
    # Since CCDF is decreasing, we need to find where CCDF crosses target_prob
    
    # Check if target_prob is within range
    if target_prob < ccdf.min() or target_prob > ccdf.max():
        return None
    
    # Find indices where we cross the target probability
    # Since CCDF is decreasing, find where it goes from above to below target_prob
    below_mask = ccdf <= target_prob
    above_mask = ccdf >= target_prob
    
    if not np.any(below_mask) or not np.any(above_mask):
        # Find closest value
        idx = np.argmin(np.abs(ccdf - target_prob))
        x_at_prob = xs[idx]
    else:
        # Find the transition point
        # Get indices where we're just above and just below
        above_indices = np.where(above_mask)[0]
        below_indices = np.where(below_mask)[0]
        
        if len(above_indices) > 0 and len(below_indices) > 0:
            # Find the last point above and first point below
            last_above_idx = above_indices[-1]
            first_below_idx = below_indices[0]
            
            # If they're adjacent, use linear interpolation
            if first_below_idx == last_above_idx + 1:
                # Linear interpolation
                y1, y2 = ccdf[last_above_idx], ccdf[first_below_idx]
                x1, x2 = xs[last_above_idx], xs[first_below_idx]
                
                if y1 != y2:
                    # Interpolate: x = x1 + (x2 - x1) * (target_prob - y1) / (y2 - y1)
                    x_at_prob = x1 + (x2 - x1) * (target_prob - y1) / (y2 - y1)
                else:
                    x_at_prob = (x1 + x2) / 2
            else:
                # Use closest value
                idx = np.argmin(np.abs(ccdf - target_prob))
                x_at_prob = xs[idx]
        else:
            idx = np.argmin(np.abs(ccdf - target_prob))
            x_at_prob = xs[idx]
    
    # Calculate margin: difference from threshold
    margin_db = x_at_prob - threshold_db
    
    return margin_db

def print_protection_margins_table(curves_data: List[Dict], protection_criteria: List[Tuple[float, float]]):
    """
    Print a table showing how many dB each curve is from each protection criterion.
    """
    if not protection_criteria or not curves_data:
        return
    
    print("\n" + "="*80)
    print("PROTECTION MARGINS TABLE")
    print("="*80)
    print("Values show: curve_INR_at_probability - criterion_threshold (dB)")
    print("Positive = above threshold (worse), Negative = below threshold (better)")
    print("="*80)
    
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
            criterion_label = f"{thr_db} dB @ {prob*100:.2f}%"
            if criterion_label not in criterion_labels:
                criterion_labels.append(criterion_label)
            
            margin = calculate_protection_margin(xs, ccdf, thr_db, prob)
            curve_margins.append(margin)
        
        margins.append(curve_margins)
    
    if not margins:
        print("No data available for margin calculation")
        return
    
    # Print header
    header = f"{'Curve':<40}"
    for crit_label in criterion_labels:
        header += f"{crit_label:>20}"
    print(header)
    print("-" * (40 + 20 * len(criterion_labels)))
    
    # Print rows
    for i, (label, curve_margins) in enumerate(zip(curve_labels, margins)):
        row = f"{label:<40}"
        for margin in curve_margins:
            if margin is not None:
                # Format with 2 decimal places
                row += f"{margin:>20.2f}"
            else:
                row += f"{'N/A':>20}"
        print(row)
    
    print("="*80 + "\n")

def plot_ccdf_inr(
    curves_to_plot: Optional[List[Tuple]] = None,
    custom_labels: Optional[Dict[Tuple, str]] = None,
    legend_loc: str = "best",
    legend_fontsize: float = 9,
    legend_ncol: int = 1,
    legend_framealpha: float = 0.9,
    show_protection_criteria: bool = True,
    protection_criteria: Optional[List[Tuple[float, float]]] = None
):
    """
    Main plotting function
    
    Parameters
    ----------
    curves_to_plot : Optional[List[Tuple]]
        List of filters for curves to plot. Format: (R, x_pos, height, clutter, location_type, custom_label)
        Use None to plot all curves
    custom_labels : Optional[Dict[Tuple, str]]
        Dictionary mapping filter tuples to custom label names
        Key: (R, x_pos, height, clutter, location_type) - without custom_label
        Value: Custom label string
    legend_loc : str
        Legend location (e.g., "best", "upper right", "lower left", "outside")
    legend_fontsize : float
        Font size for legend
    legend_ncol : int
        Number of columns in legend
    legend_framealpha : float
        Transparency of legend background (0.0 to 1.0)
    show_protection_criteria : bool
        Whether to show protection criteria lines
    protection_criteria : Optional[List[Tuple[float, float]]]
        Custom protection criteria. If None, uses PROTECTION_CRITERIA from settings
    """
    if curves_to_plot is None:
        curves_to_plot = CURVES_TO_PLOT if CURVES_TO_PLOT else []
    
    if protection_criteria is None:
        protection_criteria = PROTECTION_CRITERIA
    
    # Find all INR CSV files
    inr_files = list(OUTPUT_DIR.rglob(INR_FILE))
    
    if not inr_files:
        print(f"No INR files found in {OUTPUT_DIR}")
        return
    
    print(f"Found {len(inr_files)} INR files")
    
    # Load and organize data
    curves_data = []
    for csv_path in inr_files:
        # Get parent directory (output folder for this simulation)
        output_folder = csv_path.parent
        
        features = parse_features_from_path(output_folder)
        
        # Check if this curve should be plotted
        if curves_to_plot:
            matched = False
            matched_filter = None
            for filt in curves_to_plot:
                # Extract filter tuple without custom_label for matching
                if len(filt) == 6:
                    filter_key = filt[:5]
                else:
                    filter_key = filt
                
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
        if matched_filter and len(matched_filter) == 6 and matched_filter[5] is not None:
            # Use custom label from filter tuple
            label = matched_filter[5]
        elif custom_labels:
            # Check if there's a custom label in the dictionary
            filter_key = (
                features["R"],
                features["x"],
                features["height"],
                features["clutter"],
                features["location_type"]
            )
            label = custom_labels.get(filter_key, create_label(features))
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
    
    # Create plot
    fig, ax = plt.subplots(figsize=FIGSIZE)
    
    # Plot each curve
    for curve in curves_data:
        xs, ccdf = ecdf_to_ccdf(curve["data"])
        if xs.size > 0:
            ax.semilogy(xs, ccdf, drawstyle="steps-post", label=curve["label"], linewidth=1.5)
    
    # Add protection criteria lines
    pc_handles = []
    if show_protection_criteria:
        # Define different colors for each protection criterion
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        for idx, (thr_db, prob) in enumerate(protection_criteria):
            # Use different color for each criterion
            color = colors[idx % len(colors)]
            
            # Vertical line at threshold
            ax.axvline(thr_db, linestyle="--", linewidth=1.5, color=color, alpha=0.7)
            # Horizontal line at probability
            ax.axhline(prob, linestyle="--", linewidth=1.5, color=color, alpha=0.7)
            # Removed: intersection point marker
            
            pc_handles.append(Line2D(
                [], [], linestyle="--", color=color, linewidth=1.5,
                label=f"Protection: {thr_db} dB @ {prob*100:.2f}%"
            ))
    
    # Configure plot
    ax.set_title(TITLE_PREFIX, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(XLABEL, fontsize=12)
    ax.set_ylabel(YLABEL, fontsize=12)
    ax.set_ylim(CCDF_FLOOR, 1.0)
    ax.grid(True, which="both", alpha=0.3, linestyle=':')
    
    # Combine legends
    handles, labels = ax.get_legend_handles_labels()
    handles.extend(pc_handles)
    
    # Handle legend location
    if legend_loc == "outside":
        ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5), 
                 fontsize=legend_fontsize, ncol=legend_ncol, framealpha=legend_framealpha)
    else:
        ax.legend(handles=handles, loc=legend_loc, fontsize=legend_fontsize, 
                 ncol=legend_ncol, framealpha=legend_framealpha)
    
    # Save figure
    plots_dir = Path(__file__).parent / "plot"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = plots_dir / "ccdf_inr.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    import sys
    height = [5, 40]
    distance = [30000, 35000]
    # ===================== CONFIGURATION =====================
    # Configure which curves to plot
    # Format: (R, x_pos, height, clutter, location_type, custom_label)
    #   - R: Distance from center in meters (e.g., 2600, 3600, 6600) or None for all
    #   - x_pos: X position in meters for FIXED location (e.g., 2600, -2600) or None for all/UNIFORM
    #   - height: Earth station height in meters (e.g., 5, 40) or None for all
    #   - clutter: Clutter type ("one_end", "both_ends") or None for all
    #   - location_type: "FIXED" or "UNIFORM" or None for all
    #   - custom_label: Custom name for this curve (optional, None uses auto-generated label)
    curves_to_plot = [
        # Example 1: Compare FIXED vs UNIFORM for R=3600, height=40m, both_ends
          #(1600 + 2000, None, 40, "both_ends", "FIXED", "FIXED, h=40m, Distance = 2Km"),
          #(1600 + 2000, None, 40, "both_ends", "UNIFORM", "UNIFORM, h=40m, Distance = 2Km"),
        
        # Example 2: Compare different heights
         # (2600, 2600, 5, "both_ends", "FIXED", "Low height (5m)"),
         # (2600, 2600, 40, "both_ends", "FIXED", "High height (40m)"),
        
        # Example 3: Compare x positions
        # (3600, 3600, 40, "both_ends", "FIXED", "x = +R"),
        # (3600, -3600, 40, "both_ends", "FIXED", "x = -R"),

         #(1600 + 30000, None, 45, "both_ends", "UNIFORM", "UNIFORM, h=40m, Distance = 30Km"),
         (1600 + distance[0], None, height[0], "both_ends", "UNIFORM", f"UNIFORM, h={height[0]}m, Distance = {distance[0]/1000}Km"),
         (1600 + distance[1], None, height[0], "both_ends", "UNIFORM", f"UNIFORM, h={height[0]}m, Distance = {distance[1]/1000}Km"),
         (1600 + distance[0], None, height[1], "both_ends", "UNIFORM", f"UNIFORM, h={height[1]}m, Distance = {distance[0]/1000}Km"),
         (1600 + distance[1], None, height[1], "both_ends", "UNIFORM", f"UNIFORM, h={height[1]}m, Distance = {distance[1]/1000}Km")
         #(1600 + 45000, None, 40, "both_ends", "UNIFORM", "UNIFORM, h=40m, Distance = 45Km"),
         #(1600 + 50000, None, 40, "both_ends", "UNIFORM", "UNIFORM, h=40m, Distance = 50Km"),
        
        # Leave empty [] to plot all curves
    ]
    
    # Alternative: Use dictionary for custom labels (useful when plotting all curves)
    # Key: (R, x_pos, height, clutter, location_type)
    # Value: Custom label string
    custom_labels = {
        # Example:
        # (2600, 2600, 5, "one_end", "FIXED"): "Scenario A",
        # (2600, 2600, 40, "one_end", "FIXED"): "Scenario B",
    }
    
    # Legend configuration
    legend_location = "best"  # Options: "best", "upper right", "lower left", "upper left", 
                              #          "lower right", "right", "center left", "center right",
                              #          "lower center", "upper center", "center", "outside"
    legend_font_size = 9       # Font size for legend text
    legend_columns = 1         # Number of columns in legend (use 2 or 3 for many curves)
    legend_alpha = 0.9         # Legend background transparency (0.0 = transparent, 1.0 = opaque)
    
    # Protection criteria
    show_protection = True     # Set to False to hide protection criteria lines
    # =========================================================
    
    # Example usage scenarios - uncomment and modify as needed
    
    # Example 1: Plot all curves with default settings
    # plot_ccdf_inr()
    
    # Example 2: Plot specific curves with custom labels and legend outside
    # plot_ccdf_inr(
    #     curves_to_plot=[
    #         (2600, None, 5, None, "FIXED", "FIXED, h=5m"),
    #         (2600, None, 40, None, "FIXED", "FIXED, h=40m"),
    #     ],
    #     legend_loc="outside",
    #     legend_fontsize=10,
    #     legend_ncol=1
    # )
    
    # Example 3: Plot all curves but use custom_labels dictionary for naming
    # plot_ccdf_inr(
    #     curves_to_plot=[],  # Empty = plot all
    #     custom_labels={
    #         (2600, 2600, 5, "both_ends", "FIXED"): "Case 1",
    #         (3600, 3600, 5, "both_ends", "FIXED"): "Case 2",
    #     },
    #     legend_loc="best",
    #     legend_fontsize=9
    # )
    
    # Default: use configuration from above
    if len(sys.argv) > 1:
        print("Usage: python plot_ccdf_inr.py")
        print("Configure the script variables in the if __main__ block")
        sys.exit(0)
    
    plot_ccdf_inr(
        curves_to_plot=curves_to_plot,
        custom_labels=custom_labels if custom_labels else None,
        legend_loc=legend_location,
        legend_fontsize=legend_font_size,
        legend_ncol=legend_columns,
        legend_framealpha=legend_alpha,
        show_protection_criteria=show_protection
    )
