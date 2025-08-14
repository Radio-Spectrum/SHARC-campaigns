# campaigns/imt_to_mss/plot_ccdf_imt_sinr_ext_per_bucket.py
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except Exception:
    _HAS_PANDAS = False

# =============== USER SETTINGS =================
ENGINE = "matplotlib"         # "matplotlib" or "sharc" (stubbed)
THRESHOLD_DB = -6.0
TITLE_PREFIX = "IMT victim-side SINR (external interference)"
XLABEL = "SINR_ext (dB)"
YLABEL = "CCDF"
CCDF_FLOOR = 1e-6             # avoid zeros on log-y

# Paths relative to this file
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = BASE_DIR / "output"
PLOTS_DIR = BASE_DIR / "plots"

# Filenames to look for
SINR_FILES = ("imt_dl_sinr_ext.csv", "imt_ul_sinr_ext.csv")

# Bucket order (and exact labels)
BUCKET_ORDER = [
    "MACRO - DL (RANDOM)",
    "MACRO - DL (RANDOM_GLOBAL)",
    "MACRO - UL (RANDOM)",
    "MACRO - UL (RANDOM_GLOBAL)",
    "MICRO - DL (RANDOM)",
    "MICRO - DL (RANDOM_GLOBAL)",
    "MICRO - UL (RANDOM)",
    "MICRO - UL (RANDOM_GLOBAL)",
]
# ===============================================


def find_sinr_csvs(root: Path) -> List[Path]:
    files: List[Path] = []
    for patt in SINR_FILES:
        files.extend(root.rglob(patt))
    return files


def parse_bucket(path: Path) -> str | None:
    s = str(path).lower()
    # link
    if "uplink" in s:
        link = "UL"
    elif "downlink" in s:
        link = "DL"
    else:
        return None
    # cell type
    if "macrocell" in s:
        cell = "MACRO"
    elif "microcell" in s:
        cell = "MICRO"
    else:
        return None
    # p-mode
    if "p-random_global" in s or "p_random_global" in s:
        pmode = "RANDOM_GLOBAL"
    elif "p-random" in s or "p_random" in s:
        pmode = "RANDOM"
    else:
        return None
    return f"{cell} - {link} ({pmode})"


_Y_REGEX = re.compile(r"_y(\d+)\b")


def parse_distance_tag(path: Path) -> str | None:
    """Extract y#### tag from the directory name (e.g., y1000)."""
    m = _Y_REGEX.search(path.name) or _Y_REGEX.search(str(path))
    if not m:
        return None
    return f"y{m.group(1)}"


def _to_float_array(one_col: np.ndarray) -> np.ndarray:
    arr = np.asarray(one_col, dtype="float64").ravel()
    arr = arr[np.isfinite(arr)]
    return arr


def load_vector(csv_path: Path) -> np.ndarray:
    """Load a 1D vector of SINR (dB) from CSV with one column."""
    if _HAS_PANDAS:
        try:
            # try header=0
            df = pd.read_csv(csv_path, header=0)
            if df.shape[1] >= 1:
                vals = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().to_numpy()
                if vals.size:
                    return vals
        except Exception:
            pass
        try:
            df = pd.read_csv(csv_path, header=None)
            vals = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna().to_numpy()
            return vals
        except Exception:
            return np.array([], dtype=float)
    # numpy fallback
    try:
        vals = np.genfromtxt(csv_path, delimiter=",", dtype=float)
        return _to_float_array(vals)
    except Exception:
        return np.array([], dtype=float)


def ecdf_to_ccdf(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    x_sorted = np.sort(np.asarray(x, dtype=float))
    n = x_sorted.size
    if n == 0:
        return x_sorted, x_sorted
    cdf = np.arange(1, n + 1, dtype=float) / float(n)
    ccdf = 1.0 - cdf
    ccdf = np.maximum(ccdf, CCDF_FLOOR)
    return x_sorted, ccdf


def gather_data(files: List[Path]) -> Dict[str, Dict[str, List[np.ndarray]]]:
    """
    returns: { bucket_label: { distance_tag: [arrays...] } }
    """
    data: Dict[str, Dict[str, List[np.ndarray]]] = {b: {} for b in BUCKET_ORDER}
    skipped = 0
    for f in files:
        bucket = parse_bucket(f)
        if bucket is None:
            skipped += 1
            continue
        dist = parse_distance_tag(f.parent) or parse_distance_tag(f.parent.parent)
        if dist is None:
            skipped += 1
            continue
        vec = load_vector(f)
        if vec.size == 0:
            continue
        data[bucket].setdefault(dist, []).append(vec)
    if skipped:
        print(f"Note: skipped {skipped} files that did not match bucket/dist patterns.")
    return data


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def plot_bucket_matplotlib(
    bucket_label: str,
    dist_map: Dict[str, List[np.ndarray]],
    save_dir: Path,
) -> None:
    import matplotlib.pyplot as plt

    # sort distances by numeric value inside "y####"
    def dist_key(d: str) -> int:
        m = re.search(r"y(\d+)", d)
        return int(m.group(1)) if m else 0

    dists = sorted(dist_map.keys(), key=dist_key)

    fig, ax = plt.subplots(figsize=(9, 6))
    any_curve = False

    for dtag in dists:
        arrays = dist_map[dtag]
        if not arrays:
            continue
        any_curve = True
        x = np.concatenate(arrays, axis=0)
        xs, ccdf = ecdf_to_ccdf(x)
        # semilog-y
        ax.semilogy(xs, ccdf, drawstyle="steps-post", label=dtag)

    if not any_curve:
        print(f"[WARN] No data to plot for bucket: {bucket_label}")
        plt.close(fig)
        return

    # threshold
    ax.axvline(THRESHOLD_DB, linestyle="--", linewidth=1.5)
    ax.text(THRESHOLD_DB, 0.5, f"Threshold {THRESHOLD_DB:.0f} dB",
            rotation=90, va="center", ha="right")

    ax.set_title(f"{TITLE_PREFIX} – {bucket_label}")
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(YLABEL)
    ax.set_ylim(CCDF_FLOOR, 1.0)
    ax.grid(True, which="both", axis="both", alpha=0.3)
    ax.legend(loc="best", fontsize=9, title="Distance (y tag)")

    save_dir.mkdir(parents=True, exist_ok=True)
    out_path = save_dir / f"ccdf_imt_sinr_ext_{_slug(bucket_label)}_semilogy_{ENGINE.lower()}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved: {out_path}")


def plot_bucket_sharc(
    bucket_label: str,
    dist_map: Dict[str, List[np.ndarray]],
    save_dir: Path,
) -> None:
    # Wire your SHARC post-processor here if you have one.
    raise NotImplementedError(
        "ENGINE='sharc' selected. Plug your SHARC plotting routine into plot_bucket_sharc()."
    )


def main() -> None:
    print(f"Scanning for SINR files under: {OUTPUT_ROOT}")
    files = find_sinr_csvs(OUTPUT_ROOT)
    if not files:
        print("No imt_*_sinr_ext.csv files found. Check OUTPUT_ROOT.")
        return

    data = gather_data(files)

    # summary
    print("Series per bucket:")
    for b in BUCKET_ORDER:
        total_samples = sum(np.sum([arr.size for arr in arrs]) for arrs in data[b].values())
        print(f"  {b:30s} -> distances: {len(data[b])}, total samples: {int(total_samples)}")

    for b in BUCKET_ORDER:
        dist_map = data[b]
        if not dist_map:
            print(f"[INFO] Skipping empty bucket: {b}")
            continue
        if ENGINE.lower() == "matplotlib":
            plot_bucket_matplotlib(b, dist_map, PLOTS_DIR)
        elif ENGINE.lower() == "sharc":
            plot_bucket_sharc(b, dist_map, PLOTS_DIR)
        else:
            print(f"[ERROR] Unknown ENGINE='{ENGINE}'. Use 'matplotlib' or 'sharc'.")
            return


if __name__ == "__main__":
    main()
