from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _rotate(points: np.ndarray, angle_deg: float) -> np.ndarray:
    angle = np.deg2rad(angle_deg)
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)],
        ]
    )
    return points @ rotation.T


def _arc_with_arrow(ax, cx, cy, r, a_start_deg, a_end_deg, color="black", lw=1.0):
    """Draw an arc from a_start_deg to a_end_deg with an arrowhead at the tip."""
    angles = np.linspace(a_start_deg, a_end_deg, 80)
    xs = cx + r * np.cos(np.deg2rad(angles))
    ys = cy + r * np.sin(np.deg2rad(angles))
    ax.plot(xs, ys, color=color, linewidth=lw, zorder=5)
    ax.annotate(
        "",
        xy=(xs[-1], ys[-1]),
        xytext=(xs[-5], ys[-5]),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw * 0.9, mutation_scale=10),
        zorder=6,
    )
    return xs, ys


def plot_ngso_orbit_plane_angles() -> Path:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ngso_orbit_plane_angles.png"

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # ── Equatorial plane ────────────────────────────────────────────────────────
    eq_pts = np.array([[-4.2, -1.4], [4.2, -1.4], [2.8, 1.4], [-5.6, 1.4], [-4.2, -1.4]])
    ax.plot(eq_pts[:, 0], eq_pts[:, 1], color="black", linewidth=1.0, zorder=2)
    ax.text(-4.9, 1.55, "Equatorial plane", fontsize=11)

    # ── Orbit plane ─────────────────────────────────────────────────────────────
    base_rect = np.array([[-3.6, -3.0], [3.2, -3.0], [3.2, 3.2], [-3.6, 3.2], [-3.6, -3.0]])
    orb_plane_pts = _rotate(base_rect, 32)
    ax.plot(orb_plane_pts[:, 0], orb_plane_pts[:, 1], color="black", linewidth=1.0, zorder=2)
    ax.text(1.3, 3.75, "Orbit plane", fontsize=11)

    # ── Orbit ellipse ────────────────────────────────────────────────────────────
    theta_full = np.linspace(0, 2 * np.pi, 600)
    ell = np.column_stack([2.8 * np.cos(theta_full), 1.5 * np.sin(theta_full)])
    ell = _rotate(ell, 32)
    ax.plot(ell[:, 0], ell[:, 1], color="black", linewidth=1.2, zorder=3)

    # ── Perigee & apogee ────────────────────────────────────────────────────────
    perigee = _rotate(np.array([[2.8, 0.0]]), 32)[0]
    apogee  = _rotate(np.array([[-2.8, 0.0]]), 32)[0]
    ax.plot(perigee[0], perigee[1], marker="o", color="black", markersize=5, zorder=5)
    ax.plot(apogee[0],  apogee[1],  marker="o", color="black", markersize=5, zorder=5)
    ax.text(perigee[0] + 0.12, perigee[1] + 0.22, "Perigee", fontsize=11)
    ax.text(apogee[0]  - 0.55, apogee[1]  - 0.32, "Apogee",  fontsize=11)

    # ── Line of apsides (dashed) — apogee through O to perigee ──────────────────
    ax.plot([apogee[0], perigee[0]], [apogee[1], perigee[1]],
            color="black", linewidth=0.8, linestyle="--", zorder=2)

    # ── Orbit direction arrow near perigee ───────────────────────────────────────
    sat_t = np.deg2rad(16)
    dt    = np.deg2rad(7)
    p0 = _rotate(np.array([[2.8 * np.cos(sat_t),      1.5 * np.sin(sat_t)]]),      32)[0]
    p1 = _rotate(np.array([[2.8 * np.cos(sat_t + dt), 1.5 * np.sin(sat_t + dt)]]), 32)[0]
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.4,
                                mutation_scale=12),
                zorder=5)
    # "Orbit satellite" label — to the right, with arrow pointing to the direction arrow
    ax.annotate(
        "Orbit satellite",
        xy=p0,
        xytext=(perigee[0] + 1.15, perigee[1] - 0.30),
        fontsize=11,
        arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
        zorder=6,
    )

    # ── Origin ──────────────────────────────────────────────────────────────────
    ax.plot(0, 0, marker="o", color="black", markersize=4, zorder=5)
    ax.text(-0.25, -0.22, "O", fontsize=11)

    # ── Coordinate axes ─────────────────────────────────────────────────────────
    arr = dict(arrowstyle="-|>", color="black", lw=1.5, mutation_scale=12)
    ax.annotate("", xy=(4.5,  0.0),  xytext=(0, 0), arrowprops=arr, zorder=4)
    ax.annotate("", xy=(-3.2, -3.2), xytext=(0, 0), arrowprops=arr, zorder=4)
    ax.annotate("", xy=(0.0,  3.7),  xytext=(0, 0), arrowprops=arr, zorder=4)
    ax.text( 4.65,  0.10, "Y", fontsize=12, fontweight="bold")
    ax.text(-3.55, -3.50, "X", fontsize=12, fontweight="bold")
    ax.text( 0.12,  3.55, "Z", fontsize=12, fontweight="bold")

    # ── Line of nodes (solid, bidirectional arrows) ───────────────────────────────
    node_y  = -2.05
    node_x1 = -2.6
    node_x2 =  2.4
    ax.plot([node_x1, node_x2], [node_y, node_y],
            color="black", linewidth=1.2, zorder=3)
    for tip, base_ in [(node_x2, node_x2 - 0.9), (node_x1, node_x1 + 0.9)]:
        ax.annotate("", xy=(tip, node_y), xytext=(base_, node_y),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2,
                                    mutation_scale=10),
                    zorder=5)
    ax.text(0.5, node_y - 0.52, "Line of the nodes", fontsize=11)

    # ── RAAN arc Ω (from Y direction to ascending-node direction, at O) ──────────
    # ascending-node direction from O: angle to (node_x2, node_y)
    omega_end = np.degrees(np.arctan2(node_y, node_x2))   # ≈ −40°
    _arc_with_arrow(ax, 0, 0, 0.78, a_start_deg=0, a_end_deg=omega_end,
                    color="black", lw=1.0)
    omega_mid = np.deg2rad(omega_end / 2)
    ax.text(0.78 * np.cos(omega_mid) + 0.08,
            0.78 * np.sin(omega_mid) - 0.22,
            "Ω", fontsize=13)

    # ── Argument-of-perigee arc ω (from ascending-node dir. to perigee dir., at O) ─
    perigee_angle = np.degrees(np.arctan2(perigee[1], perigee[0]))   # ≈ 32°
    _arc_with_arrow(ax, 0, 0, 1.05, a_start_deg=omega_end, a_end_deg=perigee_angle,
                    color="black", lw=1.0)
    om_mid_deg = (omega_end + perigee_angle) / 2
    om_mid_rad = np.deg2rad(om_mid_deg)
    ax.text(1.05 * np.cos(om_mid_rad) + 0.12,
            1.05 * np.sin(om_mid_rad) + 0.12,
            "ω", fontsize=13)

    # ── Inclination arc i (at ascending node, between line-of-nodes and orbit) ───
    # At the ascending node the line-of-nodes is horizontal (0° = rightward from node).
    # The orbit plane rises above the equatorial plane; the arc spans that angle.
    asc_x, asc_y = node_x2, node_y
    r_i     = 0.80
    i_start = 90    # upward  (orbit rise direction in 2-D projection)
    i_end   = 138   # tilted  (equatorial/line-of-nodes reference direction)
    # reference arms
    for ang in (i_start, i_end):
        ax.plot([asc_x, asc_x + r_i * np.cos(np.deg2rad(ang))],
                [asc_y, asc_y + r_i * np.sin(np.deg2rad(ang))],
                color="black", linewidth=0.9, linestyle="-", zorder=4)
    _arc_with_arrow(ax, asc_x, asc_y, r_i, a_start_deg=i_start, a_end_deg=i_end,
                    color="black", lw=1.0)
    i_mid_rad = np.deg2rad((i_start + i_end) / 2)
    ax.text(asc_x + (r_i + 0.16) * np.cos(i_mid_rad),
            asc_y + (r_i + 0.16) * np.sin(i_mid_rad),
            "i", fontsize=13, fontstyle="italic")

    # ── Mean anomaly arc M (from perigee to satellite, along orbit ellipse) ────────
    # Satellite at a clearly separate position from perigee (t = 40°)
    m_sat_t = np.deg2rad(40)
    m_theta = np.linspace(0, m_sat_t, 60)
    m_arc = np.column_stack([2.8 * np.cos(m_theta), 1.5 * np.sin(m_theta)])
    m_arc = _rotate(m_arc, 32)
    ax.plot(m_arc[:, 0], m_arc[:, 1], color="black", linewidth=2.0, zorder=4)
    ax.annotate("", xy=(m_arc[-1, 0], m_arc[-1, 1]),
                xytext=(m_arc[-5, 0], m_arc[-5, 1]),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0,
                                mutation_scale=10),
                zorder=5)
    # M label: placed radially inside the arc midpoint
    m_mid_t   = np.deg2rad(20)
    m_inner   = _rotate(np.array([[1.9 * np.cos(m_mid_t), 1.0 * np.sin(m_mid_t)]]), 32)[0]
    ax.text(m_inner[0], m_inner[1], "M", fontsize=13, fontstyle="italic",
            ha="center", va="center")

    # ── Title ───────────────────────────────────────────────────────────────────
    ax.text(0.0, 5.05, "NGSO orbit plane angles",
            ha="center", fontsize=14, fontweight="bold")

    ax.set_xlim(-6.2, 6.2)
    ax.set_ylim(-5.2, 5.5)

    fig.savefig(output_file, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return output_file


if __name__ == "__main__":
    generated = plot_ngso_orbit_plane_angles()
    print(f"Figure generated at: {generated}")
