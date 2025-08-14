# campaigns/imt_to_mss/plot_ccdf_system_inr.py
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
CELLS    = ["Macro"]                          # "Macro", "Micro"
LINKS    = ["Uplink", "Downlink"]             # "Uplink", "Downlink"
PMODES   = [20, "random", "random_global"]    # 20 | "random" | "random_global"
CLUTTERS = ["both_ends"]                      # "one_end", "both_ends"

# Reference distance Ro (meters). Distance label shows Δ = y - Ro, in km.
RO_METERS = 1600

# Protection criteria lines: (threshold_dB, CCDF probability)
PROTECTION_CRITERIA: List[Tuple[float, float]] = [
    (-6.0, 3e-4),
    (-7.0, 1e-3),
    (-10.5, 2e-1),
]

# Plot appearance
ENGINE = "matplotlib"          # "matplotlib" or "sharc" (stub)
TITLE_PREFIX = "CCDF of INR"
XLABEL = "INR [dB]"
YLABEL = "P(X > x)"
CCDF_FLOOR = 1e-5              # requested floor: 1e-5
FIGSIZE = (9, 6)

# Paths
BASE_DIR   = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
PLOTS_DIR  = BASE_DIR / "plot"   # <- save under 'plot' as requested

# File to search
INR_FILE = "system_inr.csv"

# Debug: print how we parsed the first N files
DEBUG_SHOW_FIRST = 8
# =========================================================


# --------------------- helpers: normalization ---------------------

def _norm_cell_token(s: str) -> str | None:
    s = s.lower()
    if "macro" in s:
        return "macro"
    if "micro" in s:
        return "micro"
    return None

def _norm_link_token(s: str) -> str | None:
    s = s.lower()
    if "uplink" in s:
        return "ul"
    if "downlink" in s:
        return "dl"
    return None

def _norm_pmode_token(s: str) -> str | None:
    s = s.lower()
    if "p-20" in s or re.search(r"\bp[-_]20\b", s):
        return "20"
    if "p-random_global" in s or "p_random_global" in s or "p-random-global" in s:
        return "random_global"
    if "p-random" in s or "p_random" in s:
        return "random"
    # fallback: explicit capture r"p-([a-z0-9_]+)"
    m = re.search(r"p-([a-z0-9_]+)", s)
    if m:
        val = m.group(1).lower()
        if val in {"20", "random", "random_global"}:
            return val
    return None

def _norm_clutter_token(s: str) -> str | None:
    s = s.lower().replace("both-end", "both_ends").replace("both_end", "both_ends")
    if "clt-both_ends" in s or "clt_both_ends" in s:
        return "both_ends"
    if "clt-one_end" in s or "clt_one_end" in s:
        return "one_end"
    # fallback: explicit capture r"clt-([a-z_]+)"
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
        t = _norm_pmode_token(f"p-{x}" if isinstance(x, int) else f"p-{x}")
        if t: pmodes.append(t)
    clutters = []
    for x in CLUTTERS:
        t = _norm_clutter_token(f"clt-{x}")
        if t: clutters.append(t)
    if not (cells and links and pmodes and clutters):
        raise ValueError("One of your selection lists is empty after normalization.")
    return cells, links, pmodes, clutters


# --------------------- helpers: path parsing ---------------------

def parse_features_from_path(path: Path) -> Tuple[str|None, str|None, str|None, str|None]:
    """
    Parse (cell, link, pmode, clutter) from the full path string
    using tolerant substring matching.
    """
    s = str(path).lower()
    cell    = _norm_cell_token(s)
    link    = _norm_link_token(s)
    pmode   = _norm_pmode_token(s)
    clutter = _norm_clutter_token(s)
    return cell, link, pmode, clutter

# distance tag search (e.g., y2600), walk up a few ancestors
_Y_FLEX = re.compile(r"(?:(?<=^)|(?<=[_\-=/]))y(?:=)?(\d+)(?=$|[_\-/])", re.IGNORECASE)

def find_y_tag_upwards(p: Path, max_levels: int = 6) -> int | None:
    cur = p
    for _ in range(max_levels):
        m = _Y_FLEX.search(cur.name) or _Y_FLEX.search(str(cur))
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
    return (y_meters - RO_METERS) / 1000.0


# --------------- helpers: loading bracketed numbers ---------------

_BRACKET_NUM = re.compile(r"^\s*\[?\s*([-+]?\d+(?:\.\d+)?)\s*\]?\s*$")

def _parse_maybe_bracketed(s: str) -> float | None:
    m = _BRACKET_NUM.match(s)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None

def load_vector(csv_path: Path) -> np.ndarray:
    """
    Load a 1D vector of floats from system_inr.csv.
    Handles rows like "17.0" and also "[17.0]" (UPLINK quirk).
    """
    # pandas: header=0 then header=None
    if _HAS_PANDAS:
        try:
            df = pd.read_csv(csv_path, header=0)
        except Exception:
            df = None
        if df is not None and df.shape[1] >= 1:
            s = df.iloc[:, 0]
            if s.dtype == object:
                vals = [_parse_maybe_bracketed(str(v)) for v in s.tolist()]
                vals = [v for v in vals if v is not None and np.isfinite(v)]
                if vals:
                    return np.asarray(vals, dtype=float)
            else:
                vals = pd.to_numeric(s, errors="coerce").dropna().to_numpy()
                if vals.size:
                    return vals.astype(float, copy=False)
        try:
            df = pd.read_csv(csv_path, header=None)
            s = df.iloc[:, 0]
            if s.dtype == object:
                vals = [_parse_maybe_bracketed(str(v)) for v in s.tolist()]
                vals = [v for v in vals if v is not None and np.isfinite(v)]
                return np.asarray(vals, dtype=float)
            else:
                vals = pd.to_numeric(s, errors="coerce").dropna().to_numpy()
                return vals.astype(float, copy=False)
        except Exception:
            pass

    # numpy fallback (read as strings, parse with bracket support)
    try:
        raw = np.genfromtxt(csv_path, delimiter=",", dtype=str)
        if raw.ndim == 0:
            raw = np.array([raw])
        vals: List[float] = []
        for item in raw.ravel():
            f = _parse_maybe_bracketed(str(item))
            if f is not None and np.isfinite(f):
                vals.append(f)
        return np.asarray(vals, dtype=float)
    except Exception:
        return np.array([], dtype=float)


# --------------------- CCDF computation ---------------------

def ecdf_to_ccdf(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return x, x
    xs = np.sort(x)
    cdf = (np.arange(1, xs.size + 1, dtype=float)) / float(xs.size)
    ccdf = np.maximum(1.0 - cdf, CCDF_FLOOR)
    return xs, ccdf


# ---------------------- data gathering ----------------------

def find_all_inr_csvs(root: Path) -> List[Path]:
    return list(root.rglob(INR_FILE))

def gather_by_combo(files: Iterable[Path],
                    wanted_cells: List[str],
                    wanted_links: List[str],
                    wanted_pmodes: List[str],
                    wanted_clutters: List[str]
                   ) -> Dict[Tuple[str, str, str, str], Dict[str, List[np.ndarray]]]:
    """
    Returns:
      {
        (cell, link, pmode, clutter): {
            'yXXXX': [arrays...],
            ...
        }, ...
      }
    """
    data: Dict[Tuple[str, str, str, str], Dict[str, List[np.ndarray]]] = {}
    miss_feature = 0
    miss_dist = 0

    files = list(files)

    # Debug: show how we parse the first few files
    for idx, f in enumerate(files[:DEBUG_SHOW_FIRST]):
        cell_d, link_d, pm_d, clt_d = parse_features_from_path(f)
        print(f"[DEBUG PARSE] {idx+1}: {f}")
        print(f"    -> cell={cell_d}, link={link_d}, pmode={pm_d}, clutter={clt_d}")

    for f in files:
        cell, link, pmode, clutter = parse_features_from_path(f)
        if not (cell and link and pmode and clutter):
            miss_feature += 1
            continue
        if (cell not in wanted_cells or
            link not in wanted_links or
            pmode not in wanted_pmodes or
            clutter not in wanted_clutters):
            # filtered out by selection
            continue

        y_m = find_y_tag_upwards(f.parent)
        if y_m is None:
            miss_dist += 1
            continue
        dtag = f"y{y_m}"

        vec = load_vector(f)
        if vec.size == 0:
            # empty file: ignore silently
            continue

        key = (cell, link, pmode, clutter)
        data.setdefault(key, {}).setdefault(dtag, []).append(vec)

    if miss_feature or miss_dist:
        print(f"Note: skipped files summary -> feature-miss: {miss_feature}, distance-miss: {miss_dist}")
    return data


# --------------------------- plotting ---------------------------

def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

def _combo_title(cell: str, link: str, pmode: str, clutter: str) -> str:
    cell_s = "Macro" if cell == "macro" else "Micro"
    link_s = "UL" if link == "ul" else "DL"
    p_s = {"20": "20", "random": "random", "random_global": "random_global"}[pmode]
    clt_s = {"one_end": "one_end", "both_ends": "both_ends"}[clutter]
    return f"{cell_s} {link_s} – p={p_s}, clt={clt_s}"

def _dtag_to_label_km(dtag: str) -> str:
    m = re.search(r"y(\d+)", dtag, re.IGNORECASE)
    if not m:
        return dtag
    y_m = int(m.group(1))
    dk = y_to_delta_km(y_m)
    if abs(dk - round(dk)) < 1e-6:
        txt = f"{int(round(dk))} km"
    else:
        txt = f"{dk:.2f} km"
    return f"distance = {txt}"

def plot_combo_matplotlib(combo: Tuple[str, str, str, str],
                          dist_map: Dict[str, List[np.ndarray]],
                          save_dir: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    (cell, link, pmode, clutter) = combo

    # Sort distances by actual Δkm
    def dist_key(dtag: str) -> float:
        m = re.search(r"y(\d+)", dtag, re.IGNORECASE)
        return y_to_delta_km(int(m.group(1))) if m else 0.0

    dists = sorted(dist_map.keys(), key=dist_key)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    any_curve = False

    for dtag in dists:
        arrays = dist_map[dtag]
        if not arrays:
            continue
        any_curve = True
        x = np.concatenate(arrays, axis=0)
        xs, ccdf = ecdf_to_ccdf(x)
        ax.semilogy(xs, ccdf, drawstyle="steps-post", label=_dtag_to_label_km(dtag))

    if not any_curve:
        print(f"[WARN] No data to plot for combo: {combo}")
        plt.close(fig)
        return

    # Protection criteria: dashed lines + legend handles
    pc_handles = []
    for thr_db, prob in PROTECTION_CRITERIA:
        ax.axvline(thr_db, linestyle="--", linewidth=1.2)
        ax.axhline(prob,  linestyle="--", linewidth=1.0)
        label = f"Protection Criteria ({thr_db:g} dB, {prob*100:.2f}%)"
        pc_handles.append(Line2D([], [], linestyle="--", color="0.25", label=label))

    ax.set_title(f"{TITLE_PREFIX} – {_combo_title(*combo)}")
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(YLABEL)
    ax.set_ylim(CCDF_FLOOR, 1.0)
    ax.grid(True, which="both", axis="both", alpha=0.3)

    # Legend: first distances, then criteria
    handles, labels = ax.get_legend_handles_labels()
    handles.extend(pc_handles)
    labels.extend(h.get_label() for h in pc_handles)
    ax.legend(handles, labels, loc="best", fontsize=9)

    save_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"ccdf_system_inr_{_slug(_combo_title(*combo))}_semilogy_{ENGINE.lower()}.png"
    out_path = save_dir / out_name
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved: {out_path}")

def plot_combo_sharc(*args, **kwargs) -> None:
    raise NotImplementedError("ENGINE='sharc' selected – plug in your SHARC plotter here.")


# ------------------------------ main ------------------------------

def main() -> None:
    cells, links, pmodes, clutters = normalize_selection()
    print(f"Searching for {INR_FILE} in: {OUTPUT_DIR}")
    files = find_all_inr_csvs(OUTPUT_DIR)

    data = gather_by_combo(files, cells, links, pmodes, clutters)

    # Summary
    print("Series per selected combination:")
    for cell in cells:
        for link in links:
            for pmode in pmodes:
                for clutter in clutters:
                    key = (cell, link, pmode, clutter)
                    dist_map = data.get(key, {})
                    total_samples = int(sum(np.sum([arr.size for arr in arrs]) for arrs in dist_map.values()))
                    print(f"  {cell.upper():5s} / {link.upper():2s} / p={pmode:<13s} / clt={clutter:<10s}"
                          f" -> distances: {len(dist_map):2d}, samples: {total_samples}")

    # Plots
    for cell in cells:
        for link in links:
            for pmode in pmodes:
                for clutter in clutters:
                    key = (cell, link, pmode, clutter)
                    dist_map = data.get(key, {})
                    if not dist_map:
                        print(f"[INFO] Skipping empty combo: {key}")
                        continue
                    if ENGINE.lower() == "matplotlib":
                        plot_combo_matplotlib(key, dist_map, PLOTS_DIR)
                    elif ENGINE.lower() == "sharc":
                        plot_combo_sharc(key, dist_map, PLOTS_DIR)
                    else:
                        print(f"[ERROR] ENGINE='{ENGINE}' is invalid. Use 'matplotlib' or 'sharc'.")
                        return

if __name__ == "__main__":
    main()
