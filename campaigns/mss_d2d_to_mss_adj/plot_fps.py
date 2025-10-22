# plot footprints
import re
from pathlib import Path

from sharc.parameters.parameters import Parameters
from sharc.satellite.scripts.plot_footprints import plot_fp, FootPrintOpts
from sharc.support.sharc_geom import GeometryConverter

from campaigns.mss_d2d_to_mss.constants import INPUTS_DIR


def extract_load_factor(filename: str) -> float:
    """
    Extracts load factor from filename pattern like '_0.2load_'.
    Returns None if not found.
    """
    match = re.search(r"_(\d*\.?\d+)load_", filename)
    if match:
        return float(match.group(1))
    return None


def process_param_file(param_file: Path):
    print(f"\nProcessing file: {param_file}")

    # Read parameters
    parameters = Parameters()
    parameters.set_file_name(param_file)
    parameters.read_params()

    # Geometry setup
    geoconv = GeometryConverter()
    geoconv.set_reference(
        parameters.imt.topology.central_latitude,
        parameters.imt.topology.central_longitude,
        parameters.imt.topology.central_altitude,
    )

    # Plot options
    opts = FootPrintOpts(
        resolution=100,
        show_service_grid_if_possible=False,
        seed=1,
        discretize=True,
        colors=['rgb(220, 220, 220)', '#fc8d59', '#7f0000']
    )

    # MSS D2D parameters
    params = parameters.mss_d2d
    params.orbits = parameters.imt.topology.mss_dc.orbits
    params.sat_is_active_if = parameters.imt.topology.mss_dc.sat_is_active_if
    params.beam_positioning = parameters.imt.topology.mss_dc.beam_positioning
    params.beam_radius = parameters.imt.topology.mss_dc.cell_radius
    params.frequency = parameters.imt.frequency

    # Extract load factor from filename
    load_factor = extract_load_factor(param_file.name)
    if load_factor is not None:
        params.beams_load_factor = load_factor
        print(f" → Load factor set to {load_factor}")
    else:
        params.beams_load_factor = 0.2  # fallback
        print(" → Load factor not found in filename, using default 0.2")

    # Antenna check
    if parameters.imt.bs.antenna.pattern != "ITU-R-S.1528-Taylor":
        print(" ⚠️ Skipping file (unsupported antenna pattern)")
        return

    params.antenna_pattern = "ITU-R-S.1528-Taylor"
    params.antenna_s1528 = parameters.imt.bs.antenna.itu_r_s_1528

    params.sat_is_active_if.conditions = [
        "LAT_LONG_INSIDE_COUNTRY",
    ]

    # Plot
    fp = plot_fp(params, geoconv, opts)
    #fp.show()

    Path("figs").mkdir(parents=True, exist_ok=True)
    out_file = Path("figs") / f"{param_file.stem}.png"
    fp.write_image(out_file)
    print(f"Saved footprint image to {out_file}")


if __name__ == "__main__":
    yaml_files = sorted(INPUTS_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"No .yaml files found in {INPUTS_DIR}")
    else:
        for param_file in yaml_files:
            process_param_file(param_file.resolve())
