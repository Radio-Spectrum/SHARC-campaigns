from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _simulator_like_stepped_curve(
    freq_mhz: np.ndarray,
    center_mhz: float,
    tx_bw_mhz: float,
    step_levels_db: tuple[float, ...],
) -> np.ndarray:
    """Illustrative stepped mask aligned with SHARC stepped-mask region logic.

    Regions are defined from channel edges at multiples of tx_bw_mhz, similarly to
    SpectralMaskStepped region boundaries used by SHARC.
    """
    low_edge = center_mhz - tx_bw_mhz / 2
    high_edge = center_mhz + tx_bw_mhz / 2

    levels = np.full_like(freq_mhz, step_levels_db[-1], dtype=float)

    inband = (freq_mhz >= low_edge) & (freq_mhz <= high_edge)
    levels[inband] = 0.0

    for step_index, level in enumerate(step_levels_db[:-1]):
        region_low_left = low_edge - (step_index + 1) * tx_bw_mhz
        region_high_left = low_edge - step_index * tx_bw_mhz
        left_region = (freq_mhz >= region_low_left) & (freq_mhz < region_high_left)

        region_low_right = high_edge + step_index * tx_bw_mhz
        region_high_right = high_edge + (step_index + 1) * tx_bw_mhz
        right_region = (freq_mhz > region_low_right) & (freq_mhz <= region_high_right)

        levels[left_region | right_region] = level

    return levels


def plot_adjacent_channel_interference(
    dc_mss_center_mhz: float = 2162.5,
    dc_mss_bandwidth_mhz: float = 5.0,
    mss_generic_bandwidth_mhz: float = 1.25,
    offsets_mhz: tuple[float, ...] = (-5.0, -10.0, -15.0),
    step_levels_db: tuple[float, ...] = (-20.0, -35.0, -50.0, -65.0),
) -> Path:
    """Generate an illustrative figure for adjacent-channel interference geometry."""
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "adjacent_channel_interference_illustration.png"

    f_min = dc_mss_center_mhz - 25
    f_max = dc_mss_center_mhz + 10
    freq = np.linspace(f_min, f_max, 5000)

    dc_curve = _simulator_like_stepped_curve(
        freq_mhz=freq,
        center_mhz=dc_mss_center_mhz,
        tx_bw_mhz=dc_mss_bandwidth_mhz,
        step_levels_db=step_levels_db,
    )

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, constrained_layout=True)

    ax0 = axes[0]
    dc_low = dc_mss_center_mhz - dc_mss_bandwidth_mhz / 2
    dc_high = dc_mss_center_mhz + dc_mss_bandwidth_mhz / 2
    ax0.axvspan(dc_low, dc_high, alpha=0.35, color="tab:blue", label="DC-MSS occupied channel")
    ax0.axvline(dc_mss_center_mhz, linestyle="--", linewidth=1.2, color="tab:blue")

    colors = ["tab:orange", "tab:green", "tab:red"]
    for index, offset in enumerate(offsets_mhz):
        mss_center = dc_mss_center_mhz + offset
        mss_low = mss_center - mss_generic_bandwidth_mhz / 2
        mss_high = mss_center + mss_generic_bandwidth_mhz / 2
        color = colors[index % len(colors)]
        ax0.axvspan(
            mss_low,
            mss_high,
            alpha=0.35,
            color=color,
            label=f"MSS generic channel, offset {offset:+.0f} MHz",
        )
        ax0.axvline(mss_center, linestyle=":", linewidth=1.0, color=color)

    ax0.set_title("Adjacent-channel frequency arrangement")
    ax0.set_ylabel("Channel placement")
    ax0.set_yticks([])
    ax0.grid(True, linestyle=":", alpha=0.4)
    ax0.legend(loc="upper left", fontsize=9)

    ax1 = axes[1]
    ax1.plot(
        freq,
        dc_curve,
        color="tab:blue",
        linewidth=2,
        label="DC-MSS stepped spectral shape",
    )

    # DC-MSS occupied channel edges
    ax1.axvline(dc_low, linestyle="--", linewidth=1.0, color="tab:blue", alpha=0.8)
    ax1.axvline(dc_high, linestyle="--", linewidth=1.0, color="tab:blue", alpha=0.8)

    for index, offset in enumerate(offsets_mhz):
        mss_center = dc_mss_center_mhz + offset
        mss_low = mss_center - mss_generic_bandwidth_mhz / 2
        mss_high = mss_center + mss_generic_bandwidth_mhz / 2
        color = colors[index % len(colors)]
        ax1.axvspan(
            mss_low,
            mss_high,
            alpha=0.22,
            color=color,
            label=f"MSS receive bandwidth, offset {offset:+.0f} MHz",
        )

    # Region boundaries aligned to SHARC stepped-mask logic on lower side
    lower_step_1 = dc_low - 1 * dc_mss_bandwidth_mhz
    lower_step_2 = dc_low - 2 * dc_mss_bandwidth_mhz
    lower_step_3 = dc_low - 3 * dc_mss_bandwidth_mhz

    for boundary, txt in [
        (lower_step_1, "edge minus 1 BW"),
        (lower_step_2, "edge minus 2 BW"),
        (lower_step_3, "edge minus 3 BW"),
    ]:
        ax1.axvline(boundary, linestyle="--", linewidth=0.9, color="gray", alpha=0.9)

    ax1.axvspan(
        lower_step_2,
        lower_step_1,
        color="gold",
        alpha=0.10,
        label="Step region 2, simulator-like",
    )
    ax1.axvspan(
        f_min,
        lower_step_3,
        color="gray",
        alpha=0.07,
        label="Far OOB region, simulator-like",
    )

    ax1.set_title("Illustrative adjacent-channel coupling into MSS receive bandwidth")
    ax1.set_xlabel("Frequency, MHz")
    ax1.set_ylabel("Relative power, dB")
    ax1.set_ylim(-85, 5)
    ax1.grid(True, linestyle=":", alpha=0.4)
    ax1.legend(loc="upper left", fontsize=9)

    fig.suptitle(
        "DC-MSS to MSS adjacent-channel interference illustration\n"
        f"DC-MSS BW = {dc_mss_bandwidth_mhz:.2f} MHz, "
        f"MSS-ES BW = {mss_generic_bandwidth_mhz:.2f} MHz, "
        "mask regions aligned with SHARC stepped boundaries",
        fontsize=12,
    )

    fig.savefig(output_file, dpi=220)
    plt.close(fig)
    return output_file


if __name__ == "__main__":
    generated = plot_adjacent_channel_interference()
    print(f"Figure generated at: {generated}")
