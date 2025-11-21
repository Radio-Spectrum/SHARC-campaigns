from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple, Iterable
import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except Exception:
    _HAS_PANDAS = False

# ===================== USER SETTINGS =====================
# What to plot (cartesian product of these lists)
CELLS = ["Micro", "Macro"]  # "Macro", "Micro"
LINKS = ["Uplink", "Downlink"]  # "Uplink", "Downlink"
PMODES = [0.2, 20, "random_global"]  # 0.2 | 20 | "random" | "random_global"
CLUTTERS = ["both_ends"]  # "one_end", "both_ends"

# Reference distance Ro (meters). Distance label shows Δ = y - Ro, in km.
RO_METERS = 1600

# Protection criteria lines: (threshold_dB, CCDF probability)
PROTECTION_CRITERIA: List[Tuple[float, float]] = [
    (-6.0, 3e-4),
    (-7.0, 1e-3),
    (-10.5, 2e-1),
]

# Plot appearance
ENGINE = "matplotlib"  # "matplotlib" or "sharc"
TITLE_PREFIX = "CCDF of INR"
XLABEL = "INR [dB]"
YLABEL = "P(X > x)"
CCDF_FLOOR = 1e-5  # requested floor: 1e-5
FIGSIZE = (9, 6)

# Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
PLOTS_DIR = BASE_DIR / "plot"

# File to search
INR_FILE = "system_inr.csv"

# Debug: print how we parsed the first N files
DEBUG_SHOW_FIRST = 8
# =========================================================

# --------------------- Helper Functions ---------------------

def _norm_cell_token(s: str) -> str | None:
    s = s.lower()
    if "macro" in s:
        return "macro"
    if "micro" in s:
        return "micro"
    return None

def _norm_link_token(s: str) -> str | None:
    s = s.lower()
    if "uplink" in s or "ul" in s:
        return "ul"
    if "downlink" in s or "dl" in s:
        return "dl"
    return None

def _norm_pmode_token(s: str) -> str | None:
    """
    Reconhece p-modes no caminho:
      p-20, p_20, p-20pct, p_20pct  -> '20'
      p-0.2, p_0_2                  -> '0.2'
      p-random, p_random            -> 'random'
      p-random_global, p_random-global -> 'random_global'
    Usa fronteiras flexíveis para separadores de caminhos.
    """
    s = s.lower()

    # fronteiras: início/apos [_\-=/] ... fim/antes de [_\-/] ou fim da string
    sep = r"(?:(?<=^)|(?<=[_\-=/]))"
    end = r"(?=$|[_\-/])"

    # random_global / random
    if re.search(sep + r"p[-_]?random[_-]?global" + end, s):
        return "random_global"
    if re.search(sep + r"p[-_]?random" + end, s):
        return "random"

    # número (com opcional 'pct'): 20, 20pct, 0.2, 0_2
    m = re.search(sep + r"p[-_]?([0-9]+(?:[._][0-9]+)?)(?:pct)?" + end, s)
    if m:
        tok = m.group(1).replace("_", ".")  # normaliza 0_2 -> 0.2
        return tok  # devolve '20' ou '0.2' (sem converter)

    return None


def _norm_clutter_token(s: str) -> str | None:
    s = s.lower().replace("both-end", "both_ends").replace("both_end", "both_ends")
    if "clt-both_ends" in s or "clt_both_ends" in s:
        return "both_ends"
    if "clt-one_end" in s or "clt_one_end" in s:
        return "one_end"
    m = re.search(r"clt-([a-z_]+)", s)
    if m:
        val = m.group(1).lower().replace("both-end", "both_ends").replace("both_end", "both_ends")
        if val in {"both_ends", "one_end"}:
            return val
    return None

def normalize_selection() -> Tuple[List[str], List[str], List[str], List[str]]:
    cells = []
    for x in CELLS:
        t = _norm_cell_token(str(x))
        if t: cells.append(t)
    
    links = []
    for x in LINKS:
        t = _norm_link_token(str(x))
        if t: links.append(t)
    
    pmodes = []
    for x in PMODES:
        # For float values, use direct string representation
        if isinstance(x, float):
            x_str = f"{x}".replace(".", "_")  # Convert 0.2 to "0_2"
        else:
            x_str = str(x)
        t = _norm_pmode_token(f"p-{x_str}")
        if t: pmodes.append(t)
    
    clutters = []
    for x in CLUTTERS:
        t = _norm_clutter_token(f"clt-{x}")
        if t: clutters.append(t)
    
    if not (cells and links and pmodes and clutters):
        raise ValueError("One of your selection lists is empty after normalization.")
    return cells, links, pmodes, clutters

def parse_features_from_path(path: Path) -> Tuple[str|None, str|None, str|None, str|None]:
    """Parse (cell, link, pmode, clutter) from path string"""
    s = str(path).lower()
    return (
        _norm_cell_token(s),
        _norm_link_token(s),
        _norm_pmode_token(s),
        _norm_clutter_token(s)
    )

def find_y_tag_upwards(p: Path, max_levels: int = 6) -> int | None:
    """Find y-distance tag in path or parent directories"""
    cur = p
    for _ in range(max_levels):
        m = re.search(r"(?:(?<=^)|(?<=[_\-\=/]))y(?:=)?(\d+)(?=$|[_\-\/])", cur.name, re.IGNORECASE) or \
            re.search(r"(?:(?<=^)|(?<=[_\-\=/]))y(?:=)?(\d+)(?=$|[_\-\/])", str(cur), re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
        if cur.parent == cur:
            break
        cur = cur.parent
    return None

def y_to_delta_km(y_meters: int) -> float:
    """Convert y-position to km relative to Ro"""
    return (y_meters - RO_METERS) / 1000.0

def load_vector(csv_path: Path) -> np.ndarray:
    """Load INR values from CSV file, handling multiple formats"""
    # Try pandas first (more robust for various formats)
    if _HAS_PANDAS:
        try:
            # Try reading normally first
            df = pd.read_csv(csv_path, header=None)
            
            # Flatten all values and convert to float
            vals = []
            for v in df.values.ravel():
                try:
                    # Handle both bracketed strings like "[-70.81]" and plain numbers
                    s = str(v).strip()
                    if s.startswith('[') and s.endswith(']'):
                        s = s[1:-1]  # Remove brackets
                    f = float(s)
                    if np.isfinite(f):
                        vals.append(f)
                except (ValueError, TypeError):
                    continue
            
            if vals:
                return np.asarray(vals, dtype=float)
        except Exception:
            pass
    
    # Fallback to numpy for simple cases
    try:
        with open(csv_path, 'r') as f:
            content = f.read()
        
        # Handle both bracketed and non-bracketed values
        vals = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # Try parsing as bracketed value
            if line.startswith('[') and line.endswith(']'):
                try:
                    f = float(line[1:-1])
                    if np.isfinite(f):
                        vals.append(f)
                    continue
                except ValueError:
                    pass
            
            # Try parsing as regular float
            try:
                f = float(line)
                if np.isfinite(f):
                    vals.append(f)
            except ValueError:
                continue
        
        return np.asarray(vals, dtype=float)
    except Exception:
        return np.array([], dtype=float)

def ecdf_to_ccdf(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Convert empirical data to CCDF"""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return x, x
    xs = np.sort(x)
    cdf = np.arange(1, xs.size + 1, dtype=float) / float(xs.size)
    ccdf = np.maximum(1.0 - cdf, CCDF_FLOOR)
    return xs, ccdf

# ---------------------- Data Collection ----------------------

def find_all_inr_csvs(root: Path) -> List[Path]:
    """Find all INR CSV files in directory tree"""
    return list(root.rglob(INR_FILE))

def gather_by_combo(
    files: Iterable[Path],
    wanted_cells: List[str],
    wanted_links: List[str],
    wanted_pmodes: List[str],
    wanted_clutters: List[str]
) -> Dict[Tuple[str, str, str, str], Dict[str, List[np.ndarray]]]:
    """
    Organize data by combination of parameters:
    {
        (cell, link, pmode, clutter): {
            'yXXXX': [arrays...],
            ...
        }, ...
    }
    """
    data = {}
    miss_feature = miss_dist = 0

    for idx, f in enumerate(list(files)[:DEBUG_SHOW_FIRST]):
        cell, link, pmode, clutter = parse_features_from_path(f)
        print(f"[DEBUG PARSE] {idx+1}: {f}")
        print(f"    -> cell={cell}, link={link}, pmode={pmode}, clutter={clutter}")

    for f in files:
        cell, link, pmode, clutter = parse_features_from_path(f)
        if not all([cell, link, pmode, clutter]):
            miss_feature += 1
            continue
        if (cell not in wanted_cells or link not in wanted_links or
            pmode not in wanted_pmodes or clutter not in wanted_clutters):
            continue

        y_m = find_y_tag_upwards(f.parent)
        if y_m is None:
            miss_dist += 1
            continue

        vec = load_vector(f)
        if vec.size > 0:
            data.setdefault((cell, link, pmode, clutter), {}).setdefault(f"y{y_m}", []).append(vec)

    if miss_feature or miss_dist:
        print(f"Note: skipped {miss_feature} files (missing features), {miss_dist} files (missing distance)")
    return data

# --------------------------- Plotting ---------------------------

def _combo_title(cell: str, link: str, pmode: str, clutter: str) -> str:
    """Generate descriptive title for plot"""
    cell_s = "Macro" if cell == "macro" else "Micro"
    link_s = "UL" if link == "ul" else "DL"
    
    # Format percentage mode
    if pmode == "0.2":
        p_s = "0.2% (p=0.2)"
    elif pmode == "20":
        p_s = "20% (p=20)"
    else:  # random/random_global
        p_s = pmode
    
    clt_s = {"one_end": "one end", "both_ends": "both ends"}[clutter]
    return f"{cell_s} {link_s} | {p_s} | Clutter: {clt_s}"

def _dtag_to_label_km(dtag: str) -> str:
    """Convert y-distance tag to human-readable label"""
    m = re.search(r"y(\d+)", dtag, re.IGNORECASE)
    if not m:
        return dtag
    y_m = int(m.group(1))
    dk = y_to_delta_km(y_m)
    return f"Δ = {dk:.1f} km" if dk != int(dk) else f"Δ = {int(dk)} km"

def plot_combo_matplotlib(
    combo: Tuple[str, str, str, str],
    dist_map: Dict[str, List[np.ndarray]],
    save_dir: Path
) -> None:
    """Plot CCDF for one parameter combination"""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    cell, link, pmode, clutter = combo
    
    # Verify we have data to plot
    total_samples = sum(len(arr) for arr_list in dist_map.values() for arr in arr_list)
    if total_samples == 0:
        print(f"[WARN] No data to plot for combo: {combo}")
        return
    
    # Sort distances by actual Δkm
    dists = sorted(dist_map.keys(), 
                  key=lambda d: y_to_delta_km(int(re.search(r"y(\d+)", d).group(1))))
    
    fig, ax = plt.subplots(figsize=FIGSIZE)
    
    # Plot each distance
    for dtag in dists:
        arrays = dist_map[dtag]
        if not arrays:
            continue
        x = np.concatenate(arrays)
        xs, ccdf = ecdf_to_ccdf(x)
        ax.semilogy(xs, ccdf, drawstyle="steps-post", label=_dtag_to_label_km(dtag))
    
    # Add protection criteria
    pc_handles = []
    for thr_db, prob in PROTECTION_CRITERIA:
        ax.axvline(thr_db, linestyle="--", linewidth=1.2, color='gray', alpha=0.7)
        ax.axhline(prob, linestyle="--", linewidth=1.0, color='gray', alpha=0.7)
        pc_handles.append(Line2D(
            [], [], linestyle="--", color="gray",
            label=f"Protection ({thr_db}dB, {prob*100:.4f}%)"
        ))
    
    # Configure plot
    ax.set_title(f"{TITLE_PREFIX}\n{_combo_title(*combo)}", pad=20)
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(YLABEL)
    ax.set_ylim(CCDF_FLOOR, 1.0)
    ax.grid(True, which="both", alpha=0.3)
    
    # Combine legends
    handles, labels = ax.get_legend_handles_labels()
    handles.extend(pc_handles)
    ax.legend(handles=handles, loc="best", fontsize=9)
    
    # Save figure
    save_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"ccdf_inr_{cell}_{link}_p{pmode.replace('.', '_')}_clt{clutter}.png"
    fig.tight_layout()
    fig.savefig(save_dir / out_name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_dir / out_name}")

# ------------------------------ Main ------------------------------

def main() -> None:
    cells, links, pmodes, clutters = normalize_selection()
    print(f"Searching for {INR_FILE} in: {OUTPUT_DIR}")
    files = find_all_inr_csvs(OUTPUT_DIR)
    data = gather_by_combo(files, cells, links, pmodes, clutters)

    # Print summary
    print("\nData summary per combination:")
    for cell in cells:
        for link in links:
            for pmode in pmodes:
                for clutter in clutters:
                    key = (cell, link, pmode, clutter)
                    dist_map = data.get(key, {})
                    total = sum(arr.size for arr_list in dist_map.values() for arr in arr_list)
                    print(f"  {cell.upper():5} {link.upper():2} p={pmode:<8} {clutter:<10} -> "
                          f"{len(dist_map):2} distances, {total:6} samples")

    # Generate plots
    print("\nGenerating plots...")
    for cell in cells:
        for link in links:
            for pmode in pmodes:
                for clutter in clutters:
                    key = (cell, link, pmode, clutter)
                    if key in data:
                        if ENGINE.lower() == "matplotlib":
                            plot_combo_matplotlib(key, data[key], PLOTS_DIR)
                        else:
                            print(f"Unsupported engine: {ENGINE}")

if __name__ == "__main__":
    main()