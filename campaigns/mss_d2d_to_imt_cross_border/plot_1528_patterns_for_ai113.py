import numpy as np

from sharc.parameters.constants import SPEED_OF_LIGHT
from sharc.antenna.antenna_s1528 import AntennaS1528, AntennaS1528Taylor
from sharc.parameters.antenna.parameters_antenna_s1528 import ParametersAntennaS1528

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # Plot gains for ITU-R-S.1528-SECTION1.2
    # initialize antenna parameters
    param = ParametersAntennaS1528()
    param.antenna_gain = 37
    param.antenna_pattern = "ITU-R-S.1528-SECTION1.2"
    param.antenna_3_dB_bw = 4.4127

    max_psi = 30 * param.antenna_3_dB_bw / 2
    psi = np.linspace(0, max_psi, num=200)

    param.antenna_l_s = -15
    antenna = AntennaS1528(param)
    gain15 = antenna.calculate_gain(off_axis_angle_vec=psi)

    param.antenna_l_s = -20
    param.antenna_3_dB_bw = 2.19
    param.l_f = 0
    antenna = AntennaS1528(param)
    gain20 = antenna.calculate_gain(off_axis_angle_vec=psi)

    param.antenna_l_s = -25
    antenna = AntennaS1528(param)
    gain25 = antenna.calculate_gain(off_axis_angle_vec=psi)

    param.antenna_l_s = -30
    antenna = AntennaS1528(param)
    gain30 = antenna.calculate_gain(off_axis_angle_vec=psi)

    param.antenna_l_s = -35
    param.l_f = -25
    param.antenna_3_dB_bw = 1.53
    antenna = AntennaS1528(param)
    gain35 = antenna.calculate_gain(off_axis_angle_vec=psi)

    param.antenna_l_s = -35
    param.l_f = -20
    param.antenna_3_dB_bw = 1.53
    antenna = AntennaS1528(param)
    gain35_2 = antenna.calculate_gain(off_axis_angle_vec=psi)

    param.antenna_l_s = -40
    param.l_f = -25
    param.antenna_3_dB_bw = 2.0
    antenna = AntennaS1528(param)
    gain40 = antenna.calculate_gain(off_axis_angle_vec=psi)

    # Plot gains for ITU-R-S.1528-LEO
    param.antenna_pattern = "ITU-R-S.1528-LEO"

    # param.antenna_l_s = -6.75
    # antenna = AntennaS1528Leo(param)
    # gain_leo = antenna.calculate_gain(off_axis_angle_vec=psi)

    fig = plt.figure(figsize=(8, 7), facecolor='w',
                     edgecolor='k')  # create a figure object

    psi_norm = psi / (param.antenna_3_dB_bw / 2)
    # plt.plot(
    #     psi_norm,
    #     gain15 -
    #     param.antenna_gain,
    #     "-b",
    #     label="$L_S = -15$ dB")
    plt.plot(
        psi_norm,
        gain20 -
        param.antenna_gain,
        "-r",
        label="$L_S = -20$ dB")
    # plt.plot(
    #     psi_norm,
    #     gain25 -
    #     param.antenna_gain,
    #     "-g",
    #     label="$L_S = -25$ dB")
    # plt.plot(
    #     psi_norm,
    #     gain30 -
    #     param.antenna_gain,
    #     "-k",
    #     label="$L_S = -30$ dB")
    plt.plot(
        psi_norm,
        gain35 -
        param.antenna_gain,
        "-m",
        label="$L_S = -35$, $L_F= -20$ dB")
    plt.plot(
        psi_norm,
        gain35 -
        param.antenna_gain,
        "-c",
        label="$L_S = -35$ dB, $L_F = -25$ dB")
    plt.plot(
        psi_norm,
        gain40 -
        param.antenna_gain,
        "-b",
        label="$L_S = -40$ dB")
    # plt.plot(psi_norm, gain_leo - param.antenna_gain,
    #          "-c", label="$L_S = -6.75$ dB (R1.3 - LEO)")

    # Plot gains for ITU-R-S.1528-LEO
    # initialize antenna parameters
    param = ParametersAntennaS1528()
    param.antenna_gain = 35
    param.antenna_pattern = "ITU-R-S.1528-LEO"
    param.antenna_3_dB_bw = 1.6
    psi = np.linspace(0, 20, num=1000)

    # param.antenna_l_s = -6.75
    # antenna = AntennaS1528Leo(param)
    # gain_leo = antenna.calculate_gain(off_axis_angle_vec=psi)

    # fig = plt.figure(figsize=(8, 7), facecolor='w',
    #                  edgecolor='k')  # create a figure object
    # psi_norm = psi / (param.antenna_3_dB_bw / 2)
    # plt.plot(psi_norm, gain_leo, "-b", label="$L_S = -6.75$ dB")

    # plt.ylim((-40, 10))
    # plt.xlim((0, np.max(psi_norm)))
    # plt.xticks(np.arange(np.floor(np.max(psi_norm))))
    # plt.title("ITU-R S.1528-0 LEO antenna radiation pattern")
    # plt.xlabel(r"Relative off-axis angle, $\psi/\psi_{3dB}$")
    # plt.ylabel(r"Gain relative to $G_{max}$ [dB]")
    # plt.legend(loc="upper right")
    # plt.grid()

    # Section 1.4 (Taylor) - Compare to Fig 6
    frequency = 12000  # MHz
    bandwidth = 0  # MHz
    antenna_gain = 0  # dBi
    slr = 20  # dB
    n_side_lobes = 4
    lamb = (SPEED_OF_LIGHT / 1e6) / (frequency - bandwidth / 2)
    beam_radius = 350  # km
    sat_altitude = 1446  # km
    a = np.arctan(beam_radius / (sat_altitude))  # radians
    l_r = 0.74 * lamb / np.sin(a)
    l_t = l_r
    params_rolloff_7 = ParametersAntennaS1528(
        antenna_gain=0,
        frequency=12000,
        bandwidth=10,
        slr=20,
        n_side_lobes=4,
        l_r=l_r,
        l_t=l_t,
    )

    # Create an instance of AntennaS1528Taylor
    antenna_rolloff_7 = AntennaS1528Taylor(params_rolloff_7)

    # Define phi angles from 0 to 60 degrees for plotting
    theta_angles = np.arange(0, 54.3, 0.5)

    # Calculate gains for each phi angle at a fixed theta angle (e.g., theta=0)
    gain_rolloff_7 = antenna_rolloff_7.calculate_gain(
        off_axis_angle_vec=theta_angles,
        theta_vec=np.zeros_like(theta_angles))

    l_r = 0.64 * lamb / np.sin(a)
    l_t = l_r
    params_rolloff_5 = ParametersAntennaS1528(
        antenna_gain=0,
        frequency=12000,
        bandwidth=10,
        slr=20,
        n_side_lobes=4,
        l_r=l_r,
        l_t=l_t,
    )

    # Create an instance of AntennaS1528Taylor
    antenna_rolloff_5 = AntennaS1528Taylor(params_rolloff_5)

    gain_rolloff_5 = antenna_rolloff_5.calculate_gain(
        off_axis_angle_vec=theta_angles,
        theta_vec=np.zeros_like(theta_angles))

    l_r = l_t = 1.6  # m
    antenna_gain = 34.1  # dBi
    slr = 20
    n_side_lobes = 4
    params_r14 = ParametersAntennaS1528(
        antenna_gain=antenna_gain,
        frequency=2000,
        bandwidth=0,
        slr=slr,
        n_side_lobes=n_side_lobes,
        l_r=l_r,
        l_t=l_t,
    )

    # Create an instance of AntennaS1528Taylor
    antenna_r14 = AntennaS1528Taylor(params_r14)

    gain_r14 = antenna_r14.calculate_gain(
        off_axis_angle_vec=theta_angles,
        theta_vec=np.zeros_like(theta_angles))

    # Plot the antenna gain as a function of phi angle
    # plt.figure(figsize=(10, 6))
    # plt.plot(theta_angles, gain_rolloff_3, label='roll_off=3')
    # plt.plot(theta_angles, gain_rolloff_5, label='roll_off=5')
    plt.plot(theta_angles, gain_r14 - antenna_gain, label='Sys3 - Rec. 1.4')
    # plt.xlabel('Theta (degrees)')
    # plt.ylabel('Gain (dB)')
    # plt.title('Normalized Antenna - Section 1.4')
    # plt.legend()
    # plt.xticks(np.arange(0, 60, 10))
    # plt.minorticks_on()
    # plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(2))
    # plt.grid(True, which='both')

    plt.ylim((-65, 10))
    plt.yticks(np.arange(-65, 11, 5))
    plt.xlim((0, np.max(psi)))
    plt.xticks(np.arange(0, np.max(psi_norm), 5))
    plt.title("ITU-R S.1528-0 antenna radiation pattern")
    plt.xlabel(r"Off-axis angle, $\psi/\psi_{3dB}$")
    plt.xlabel(r"Off-axis angle, $\psi$")
    plt.ylabel(r"Gain relative to $G_{max}$ [dB]")
    plt.legend(loc="upper right")
    plt.grid()

    plt.show()
