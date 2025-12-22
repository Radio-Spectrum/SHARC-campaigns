import numpy as np
from sharc.antenna.antenna_s1528 import AntennaS1528
from pathlib import Path
from sharc.parameters.parameters_mss_d2d import ParametersMssD2d
from sharc.parameters.parameters import Parameters
import matplotlib.pyplot as plt
from sharc.satellite.scripts.plot_footprints import plot_fp, FootPrintOpts
from sharc.support.sharc_geom import CoordinateSystem
from sharc.satellite.utils.sat_utils import sat_elevation_to_offaxis, offaxis_to_sat_elevation, earth_arc_length_from_nadir
from campaigns.ast_mss_d2d_to_imt_cpe.constants import INPUTS_DIR

MY_PATH = Path(__file__).resolve().parent

EARTH_RADIUS_M = 6371e3

def plot_antenna():
    parameters = ParametersMssD2d()
    param_file = MY_PATH.parent.parent / "from-docs/system/mss-dc/system-4.698-960MHz-block2.690km.yaml"
    parameters.load_parameters_from_file(param_file)
    # parameters.read_params()
    ant_params = parameters.antenna
    # ant = AntennaFactory.create_antenna(ant_params, 0.0, 0.0)
    antenna_high = AntennaS1528(ant_params.antenna_system_4.antenna_parameters_high)
    antenna_low = AntennaS1528(ant_params.antenna_system_4.antenna_parameters_low)
    off_axis_angle = np.linspace(0, 60, num=int(1e4))
    gains = antenna_high.calculate_gain(
        off_axis_angle_vec=off_axis_angle
    )
    idx_4dB = np.where(gains <= ant_params.antenna_system_4.antenna_parameters_high.antenna_gain - 4.0)[0][0]
    angle_4dB = off_axis_angle[idx_4dB]
    g = gains[idx_4dB]
    print("3dB angle: ", f"{off_axis_angle[np.where(
        gains <= ant_params.antenna_system_4.antenna_parameters_high.antenna_gain - 3.0)[0][0]]:.2f}")
    print("4dB angle: ", angle_4dB)
    print("for gain of: ", g)
    print("when it should be eq:", ant_params.antenna_system_4.antenna_parameters_high.antenna_gain - 4.0)
    h = parameters.orbits[0].perigee_alt_km * 1e3  # in meters
    r = np.tan(np.deg2rad(angle_4dB)) * h
    print("resulting in radius of: ", r)

    low_elev_gains = antenna_low.calculate_gain(
        off_axis_angle_vec=off_axis_angle
    )
    idx_4dB = np.where(low_elev_gains <= ant_params.antenna_system_4.antenna_parameters_low.antenna_gain - 4.0)[0][0]
    angle_4dB = off_axis_angle[idx_4dB]
    g = low_elev_gains[idx_4dB]

    print("---- Low Elevation Antenna ----")

    print("3dB angle: ", f"{off_axis_angle[
        np.where(low_elev_gains <= ant_params.antenna_system_4.antenna_parameters_low.antenna_gain - 3.0)[0][0]]:.2f}")
    print("4dB angle: ", angle_4dB)
    print("for gain of: ", g)
    print("when it should be eq:", ant_params.antenna_system_4.antenna_parameters_low.antenna_gain - 4.0)
    h = parameters.orbits[0].perigee_alt_km * 1e3  # in meters
    r = np.tan(np.deg2rad(angle_4dB)) * h
    print("resulting in radius of: ", r)

    plt.figure(figsize=(6, 6))
    plt.plot(np.concatenate((-off_axis_angle[::-1], off_axis_angle)), np.concatenate((gains[::-1], gains)))
    plt.plot(np.concatenate((-off_axis_angle[::-1], off_axis_angle)), np.concatenate((low_elev_gains[::-1], low_elev_gains)))
    plt.xlabel('off axis angle (degrees)')
    plt.ylabel('Gain (dB)')
    plt.xticks(np.arange(-100, 100, 20))
    plt.xlim((-75, 75))
    plt.ylim((np.min((gains, low_elev_gains)) - 5, np.max((gains, low_elev_gains)) + 5))
    plt.legend(['Nadir to 50deg Elevation', '50deg Elevation and below'])
    # plt.minorticks_on()
    # plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(2))
    # plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(2.5))
    plt.grid(True, which='both')

    plt.show()

def plot_fps():
    # pars = [
    #     "parameter_new_mss_d2d_100max_beams_12exclusion_1.0load_uplink_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block1.520km",
    #     "parameter_new_mss_d2d_100max_beams_48exclusion_1.0load_uplink_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block1.520km",
    #     "parameter_new_mss_d2d_150max_beams_12exclusion_1.0load_uplink_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block1.520km",
    #     "parameter_new_mss_d2d_150max_beams_48exclusion_1.0load_uplink_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block1.520km",
    #     "parameter_new_mss_d2d_50max_beams_12exclusion_1.0load_uplink_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block1.520km",
    #     "parameter_new_mss_d2d_50max_beams_48exclusion_1.0load_uplink_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block1.520km",
    # ]
    # print(list(INPUTS_DIR.iterdir()))
    # pars = [x for x in INPUTS_DIR.iterdir() if "parameter_" in str(x) and "downlink" in str(x)]
    pars = [x for x in INPUTS_DIR.iterdir() if "parameter_" in str(x)]

    if len(pars) == 0:
        print(f"No parameter files found in {INPUTS_DIR}")
        return

    for i, par in enumerate(pars[:1]):
        parameters = Parameters()
        param_file = INPUTS_DIR / par
        parameters.set_file_name(param_file)
        parameters.read_params()
        params = parameters.mss_d2d

        params.propagate_parameters()
        params.validate("opa")

        coord_sys = CoordinateSystem()

        sys_lat = parameters.imt.topology.central_latitude
        sys_long = parameters.imt.topology.central_longitude
        sys_alt = parameters.imt.topology.central_altitude

        coord_sys.set_reference(
            sys_lat, sys_long, sys_alt
        )

        opts = [
            # FootPrintOpts(
            #     seed=20,
            # ),
            FootPrintOpts(
                seed=24,
                resolution=1,
                show_service_grid_if_possible=True,
                # step=[3, 1, 3, 14],
            ),
            FootPrintOpts(
                seed=24,
                resolution=200,
                # show_service_grid_if_possible=True,
                step=[3, 1, 3, 14],
            ),
            # FootPrintOpts(
            #     seed=24,
            #     resolution=1,
            #     show_service_grid_if_possible=True,
            #     # step=[3, 1, 3, 14],
            # ),
            # FootPrintOpts(
            #     seed=24,
            #     resolution=200,
            #     # show_service_grid_if_possible=True,
            #     step=[3, 1, 3, 14],
            # ),
            # FootPrintOpts(
            #     seed=25,
            #     resolution=1,
            #     show_service_grid_if_possible=True,
            #     # step=[3, 1, 3, 14],
            # ),
            # FootPrintOpts(
            #     seed=25,
            #     resolution=200,
            #     # show_service_grid_if_possible=True,
            #     step=[3, 1, 3, 14],
            # ),
        ]

        fps_path = Path("fps")
        fps_path.mkdir(exist_ok=True)
        print(f"Plotting fps in {fps_path}")
        # Path(f"fps/{par}").mkdir(exist_ok=True)
        fig = plot_fp(params, coord_sys, opts[0])
        # fig.show()
        # fig.write_image(f"fps/{par}/grid-1.png")
        fig.write_html(f"fps/grid-{i}.html")
        params.beams_load_factor = 1.0
        fig = plot_fp(params, coord_sys, opts[1])
        fig.write_html(f"fps/fp-{i}.html")
        # if par == pars[0]:
        # fig.show()
        # fig.write_image(f"fps/{par}/fp-1.png")
        # fig = plot_fp(params, coord_sys, opts[2])
        # fig.write_image(f"fps/{par}/grid-2.png")
        # fig.write_html(f"fps/{par}/grid-2.html")
        # fig = plot_fp(params, coord_sys, opts[3])
        # fig.write_image(f"fps/{par}/fp-2.png")
        # fig.write_html(f"fps/{par}/fp-2.html")
        # fig = plot_fp(params, coord_sys, opts[4])
        # fig.write_image(f"fps/{par}/grid-3.png")
        # fig.write_html(f"fps/{par}/grid-3.html")
        # fig = plot_fp(params, coord_sys, opts[5])
        # fig.write_image(f"fps/{par}/fp-3.png")
        # fig.write_html(f"fps/{par}/fp-3.html")

def plot_pfd_analysis():
    parameters = ParametersMssD2d()
    param_file = MY_PATH.parent.parent / "from-docs/system/mss-dc/system-4.698-960MHz-block2.690km.yaml"
    parameters.load_parameters_from_file(param_file)
    # calculate slant range
    sat_altitude = parameters.orbits[0].apogee_alt_km * 1000
    # beam_radius_offaxis_angle = np.arctan(beam_radius_nadir / (sat_altitude)) * 180.0 / np.pi
    # print("beam radius offaxis angle: ", beam_radius_offaxis_angle)
    tx_power_density = parameters.tx_power_density  # in dBW/Hz
    power_backoff_dB = 10.0
    # cell_edge_rolloff_dB = 4.0

    def get_slant_range(beam_ground_elev: float | np.ndarray, sat_altitude: float | np.ndarray) -> float:
        offaxis_angle = sat_elevation_to_offaxis(beam_ground_elev, sat_altitude)
        phi_rad = np.deg2rad(offaxis_to_sat_elevation(offaxis_angle, sat_altitude) + 90.0)
        central_angle_rad = np.pi - phi_rad - np.deg2rad(offaxis_angle)
        slant_range = np.sqrt(
            (EARTH_RADIUS_M + sat_altitude)**2 + EARTH_RADIUS_M**2 -
            2 * (EARTH_RADIUS_M + sat_altitude) * EARTH_RADIUS_M * np.cos(central_angle_rad))
        return slant_range

    # plot PFD per beam elevation
    import matplotlib.pyplot as plt

    beam_ground_elevs = np.arange(20.0, 90.0, 1.0)
    actual_eipr = np.array([34.6 if e >= 50.0 else 40.0 for e in beam_ground_elevs]) + tx_power_density + 60  # in dBW/Hz to dBW/MHz
    beam_radius_offaxis_angle = np.array([1.85 if e >= 50.0 else 1.02 for e in beam_ground_elevs])
    # beam_radius_offaxis_angle = np.ones_like(beam_ground_elevs) * 1.85
    cell_edge_rolloff_dB = np.array([4.0 if e >= 50.0 else 4.0 for e in beam_ground_elevs])
    # cell_edge_rolloff_dB = np.ones_like(beam_ground_elevs) * 4.0
    slant_ranges = get_slant_range(beam_ground_elevs, sat_altitude)
    pfd_per_beam_elev = actual_eipr - 10.0 * np.log10(4.0 * np.pi * slant_ranges**2)  # in dBW/m2.MHz
    cell_edge_offaxis = sat_elevation_to_offaxis(beam_ground_elevs, sat_altitude) + beam_radius_offaxis_angle
    beam_ground_elevs_cell_edge = offaxis_to_sat_elevation(cell_edge_offaxis, sat_altitude)
    slant_range_cell_edge = get_slant_range(beam_ground_elevs_cell_edge, sat_altitude)
    pfd_per_beam_elev_cell_edge = (actual_eipr - cell_edge_rolloff_dB) - 10.0 * np.log10(4.0 * np.pi * slant_range_cell_edge**2)

    plt.figure(figsize=(8, 6))
    plt.plot(beam_ground_elevs, pfd_per_beam_elev, label='PFD before backoff')
    plt.plot(beam_ground_elevs, pfd_per_beam_elev - power_backoff_dB, label=f'PFD after backoff ({power_backoff_dB} dB)')
    plt.plot(beam_ground_elevs, pfd_per_beam_elev_cell_edge, linestyle=':', label='PFD at cell edge before backoff')
    plt.plot(beam_ground_elevs, pfd_per_beam_elev_cell_edge - power_backoff_dB, linestyle=':', label='PFD at cell edge after backoff')
    plt.xlabel('Beam Ground Elevation Angle (degrees)', fontsize=14)
    plt.ylabel('PFD (dBW/m².MHz)', fontsize=14)
    plt.title('PFD vs Beam Ground Elevation Angle', fontsize=16)
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.axhline(y=-115.0, color='r', linestyle='--', label='PFD Limit (-114.93 dBW/m².MHz)')
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig("pfd_per_beam_elevation.png", dpi=300)
    # plt.show()

    # Now we calculate the beam strength at ground level for each elevation
    arc_len = earth_arc_length_from_nadir(
        sat_elevation_to_offaxis(beam_ground_elevs, sat_altitude),
        sat_altitude)

    arc_len_edge = earth_arc_length_from_nadir(
        sat_elevation_to_offaxis(beam_ground_elevs, sat_altitude) + beam_radius_offaxis_angle,
        sat_altitude)

    beam_stretch = arc_len_edge - arc_len  # in meters

    plt.figure(figsize=(8, 6))
    plt.plot(beam_ground_elevs, beam_stretch / 1e3)
    plt.xlabel('Beam Ground Elevation Angle (degrees)', fontsize=14)
    plt.ylabel('Beam Radius (km @ major axis)', fontsize=14)
    plt.title('Beam Radius vs Beam Ground Elevation Angle', fontsize=16)
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig("beam_radius.png", dpi=300)
    plt.show()
if __name__ == "__main__":
    plot_antenna()
    # plot_fps()
    plot_pfd_analysis()
