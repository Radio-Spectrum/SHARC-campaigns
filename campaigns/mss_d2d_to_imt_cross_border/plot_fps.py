# plot footprints
from sharc.parameters.parameters import Parameters
from sharc.satellite.scripts.plot_footprints import plot_fp, FootPrintOpts
from sharc.support.sharc_geom import GeometryConverter

from campaigns.mss_d2d_to_imt_cross_border.run import INPUTS_DIR

if __name__ == "__main__":
    script_dir = INPUTS_DIR
    param_file = script_dir / "parameter_mss_d2d_to_imt_cross_border_36.675km_0.2load_dl.yaml"
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
        show_service_grid_if_possible=True,
        seed=1
    )
    fp = plot_fp(parameters.mss_d2d, geoconv, opts)
    fp.show()
