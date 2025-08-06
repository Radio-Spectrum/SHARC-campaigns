# plot footprints
from sharc.parameters.parameters import Parameters
from sharc.satellite.scripts.plot_footprints import plot_fp, FootPrintOpts
from sharc.support.sharc_geom import GeometryConverter

from campaigns.mss_d2d_to_eess.constants import INPUTS_DIR

from pathlib import Path

if __name__ == "__main__":
    # print("INPUTS_DIR", INPUTS_DIR)
    names = [
        "parameter_mss_d2d_to_eess_mss_mask_1load_uniform_elev_eess.2200-2290MHz.system-D.yaml"
    ]
    for param_name in names:
        param_file = INPUTS_DIR / param_name
        # param_file = script_dir / "../input/parameters_mss_d2d_to_imt_cross_border_0km_random_pointing_1beam_dl.yaml"
        param_file = param_file.resolve()
        print("File at:")
        print(f"  '{param_file}'")

        parameters = Parameters()
        parameters.set_file_name(param_file)
        parameters.read_params()

        geoconv = GeometryConverter()

        geoconv.set_reference(
            parameters.imt.topology.central_latitude,
            parameters.imt.topology.central_longitude,
            parameters.imt.topology.central_altitude,
        )
        opts = FootPrintOpts(
            resolution=100,
            show_service_grid_if_possible=False,
            seed=1,
            discretize=True,
            colors=['rgb(220, 220, 220)', '#fc8d59', '#7f0000']
        )
        params = parameters.mss_d2d
        params.orbits = parameters.imt.topology.mss_dc.orbits
        params.sat_is_active_if = parameters.imt.topology.mss_dc.sat_is_active_if
        params.beam_positioning = parameters.imt.topology.mss_dc.beam_positioning
        params.beam_radius = parameters.imt.topology.mss_dc.cell_radius
        params.frequency = parameters.imt.frequency
        # params.beams_load_factor = parameters.imt.bs.load_probability
        params.beams_load_factor = 1.0
        if parameters.imt.bs.antenna.pattern != "ITU-R-S.1528-Taylor":
            raise ValueError("Antenna pattern not supported by this plot script")
        params.antenna_pattern = "ITU-R-S.1528-Taylor"
        params.antenna_s1528 = parameters.imt.bs.antenna.itu_r_s_1528

        params.sat_is_active_if.conditions = [
            "LAT_LONG_INSIDE_COUNTRY",
        ]
        fp = plot_fp(params, geoconv, opts)
        fp.show()

        # Path("figs").mkdir(parents=True, exist_ok=True)
        # fp.write_image(f"figs/{param_name}.png")

