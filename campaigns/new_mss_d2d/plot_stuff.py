import numpy as np
from sharc.antenna.antenna_factory import AntennaFactory
from pathlib import Path
from sharc.parameters.parameters import Parameters
import matplotlib.pyplot as plt
from sharc.satellite.scripts.plot_footprints import plot_fp, FootPrintOpts
from sharc.support.sharc_geom import CoordinateSystem


def plot_antenna():
    parameters = Parameters()
    param_file = Path(
        "/home/artistreak/projects/Radio-Spectrum/SHARC-campaigns/campaigns/new_mss_d2d/input/parameter_new_mss_d2d_downlink.yaml"
    )
    parameters.set_file_name(param_file)
    parameters.read_params()
    ant_params = parameters.mss_d2d.antenna
    ant = AntennaFactory.create_antenna(ant_params, 0.0, 0.0)
    off_axis_angle = np.linspace(0, 60, num=int(3e4))
    gains = ant.calculate_gain(
        off_axis_angle_vec=off_axis_angle
    )
    idx = np.where(gains <= ant_params.gain - 4.0)[0][0]
    angle_4dB = off_axis_angle[idx]
    g = gains[idx]
    print("4dB angle: ", angle_4dB)
    print("for gain of: ", g)
    print("when it should be eq:", ant_params.gain - 4.0)
    r = np.tan(np.deg2rad(angle_4dB)) * 520e3
    print("resulting in radius of: ", r)

    plt.figure(figsize=(6, 6))
    plt.plot(np.concatenate((-off_axis_angle[::-1], off_axis_angle)), np.concatenate((gains[::-1], gains)))
    plt.xlabel('off_axis_angle (degrees)')
    plt.ylabel('Gain (dB)')
    plt.xticks(np.arange(-100, 100, 20))
    plt.xlim((-100, 100))
    plt.ylim((-40, 40))
    # plt.minorticks_on()
    # plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(2))
    # plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(2.5))
    plt.grid(True, which='both')

    plt.show()

def plot_fps():
    parameters = Parameters()
    param_file = Path(
        "/home/artistreak/projects/Radio-Spectrum/SHARC-campaigns/campaigns/new_mss_d2d/input/parameter_new_mss_d2d_downlink.yaml"
    )
    parameters.set_file_name(param_file)
    parameters.read_params()
    params = parameters.mss_d2d

    params.propagate_parameters()
    params.validate("opa")

    coord_sys = CoordinateSystem()

    sys_lat = -14.5
    sys_long = -52
    sys_alt = 1200

    coord_sys.set_reference(
        sys_lat, sys_long, sys_alt
    )

    opts = [
        # FootPrintOpts(
        #     seed=20,
        # ),
        FootPrintOpts(
            seed=23,
            resolution=1,
            show_service_grid_if_possible=True,
            # step=[3, 1, 3, 14],
        ),
        FootPrintOpts(
            seed=23,
            resolution=200,
            # show_service_grid_if_possible=True,
            step=[3, 1, 3, 14],
        ),
        # FootPrintOpts(
        #     seed=24,
        #     resolution=200,
        #     # show_service_grid_if_possible=True,
        #     step=[3, 1, 3, 14],
        # ),
        # FootPrintOpts(
        #     seed=25,
        #     resolution=200,
        #     # show_service_grid_if_possible=True,
        #     step=[3, 1, 3, 14],
        # ),
    ]

    for opt in opts:
        fig = plot_fp(params, coord_sys, opt)
        # fig.write_image(f"fp.png")
        fig.show()

if __name__ == "__main__":
    plot_antenna()
    # plot_fps()
