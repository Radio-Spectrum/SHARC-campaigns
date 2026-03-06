import numpy as np
from itertools import product
import argparse
import re as re
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

from campaigns.system4_mss_d2d_to_imt_pfd.constants import (
    CAMPAIGN_DIR,
    IMT_UE_TYPE,
    MSS_D2D_LOAD_FACTOR,
    IMT_FREQUENCIES_MHZ,
    IMT_FREQ_TO_IDS_MAP,
    get_specific_pattern,
    get_readable
)
from campaigns.system4_mss_d2d_to_imt_pfd.generate_inputs import (
    campaign_parameters
)

# used to cut off the CCDF tails
cutoff_percentage = 1e-6

# output_ast_mss_d2d_to_imt_cpe_24exclusion_0.2load_imt-cpe_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block2.690km_2025-11-10_01
output_dir_pattern = re.compile(
    r".*/output_system4_mss_d2d_to_imt_pfd_(\d+)exclusion_(\d+)beam_elev_(\d+\.\d+)power_backoff_(\d+)load_.*"
)

parser = argparse.ArgumentParser(description='Generate simulation plots')
parser.add_argument('--auto_open', action='store_true', default=False,
                    help='Open the generated HTML plots automatically')

args = parser.parse_args()
auto_open = args.auto_open

# Choose what to plot
imt_ue_types = campaign_parameters['imt_ue_type']
imt_frequencies_mhz = campaign_parameters['imt_frequencies_mhz']
use_phased_array = campaign_parameters['use_phased_array']
pwr_ctrl_zone_margin_from_border = campaign_parameters['pwr_ctrl_zone_margin_from_border']
min_beam_ground_elevs_deg = campaign_parameters['min_beam_ground_elevs_deg']
exclusion_margins_km = campaign_parameters['exclusion_margins_km']
power_backoffs = campaign_parameters['power_backoffs']
load_factors = campaign_parameters['load_factors']
propagation_models = campaign_parameters['propagation_models']
imt_bandwidth_mhz = campaign_parameters['imt_bandwidth_mhz']

scenario_params = [
    imt_ue_types,
    imt_frequencies_mhz,
    min_beam_ground_elevs_deg,
    exclusion_margins_km,
    power_backoffs,  # power backoff dB
    load_factors,
    propagation_models,
]

# Samples to plot CCDF from
attributes_to_plot = [
    # ("imt_system_antenna_gain", "cdf"),
    # ("imt_system_path_loss", "cdf"),
    ("system_imt_antenna_gain", "cdf"),
    # ("imt_dl_inr", "cdf"),
    # ("imt_ul_inr", "cdf"),
    ("imt_dl_inr", "ccdf"),
    ("imt_dl_pfd", "ccdf"),
    ("imt_dl_interf_power", "ccdf"),
    # ("imt_ul_inr", "ccdf"),
]

samples_for_ccdf = [attr[0] for attr in attributes_to_plot if attr[1] == "ccdf"]
samples_for_cdf = [attr[0] for attr in attributes_to_plot if attr[1] == "cdf"]

def linestyle_getter(results):
    """
    Determine the line style for plotting based on the results' output directory.

    Parameters
    ----------
    results : Results
        The results object containing the output directory information.

    Returns
    -------
    str
        The line style to use for plotting (e.g., 'dash' or 'solid').
    """
    match = output_dir_pattern.match(results.output_directory)
    if not match:
        return "solid"

    exclusion_dist, elev, pwrbo, lf = match.groups()
    i = 3
    styles = ["solid", "dot", "dash", "dashdot"]

    pwr_backoff_strs = [str(p) for p in power_backoffs]
    for i, p in enumerate(pwr_backoff_strs):
        if pwrbo == p:
            return styles[i]
    return "solid"

# We want one plot per frequency
for imt_frequency_mhz in campaign_parameters['imt_frequencies_mhz']:
    campaign_ouput_dir = CAMPAIGN_DIR / f"output_{int(imt_frequency_mhz)}"
    print("Getting results from", campaign_ouput_dir)
    # for (
    #     imt_ue_type,
    #     _,  # ignore imt frequency from combination
    #     beam_elev,
    #     exclusion_margin_km,
    #     pwr_boff,
    #     lf,
    #     prop,
    # ) in product(*scenario_params):

    post_processor = PostProcessor()

    imt_id = IMT_FREQ_TO_IDS_MAP[imt_frequency_mhz]["imt_id"]
    mss_d2d_id = IMT_FREQ_TO_IDS_MAP[imt_frequency_mhz]["mss_id"]

    # Get plots specific to the frequency band
    ccdf_results = Results.load_many_from_dir(
        campaign_ouput_dir,
        filter_fn=lambda s: str(int(imt_frequency_mhz)) + "mhz" in str(s),
        only_latest=True,
        only_samples=samples_for_ccdf)

    cdf_results = Results.load_many_from_dir(
        campaign_ouput_dir,
        # filter_fn=lambda x: "mss_d2d_to_eess" in x,
        filter_fn=lambda s: str(int(imt_frequency_mhz)) + "mhz" in str(s),
        only_latest=True,
        only_samples=samples_for_cdf)

    post_processor.add_results_linestyle_getter(linestyle_getter)

    # Convert interferece power to PFD
    # This is used to calculute aggregate PFD as the simulator generates PDF per interferer
    for res in ccdf_results:
        if hasattr(res, "imt_dl_interf_power"):
            imt_dl_interf_power_samples = np.array(res.imt_dl_interf_power)
            # NOTE: Make sure all the parameters used here are aligned with the campaign settings!!
            imt_freq_mhz = 758.0  # MHz
            imt_bw_mhz = 5.0  # MHz
            guard_band_fraction = 0.1  # 10% guard band
            # UE band calculated from the number PRBs
            ue_bandwidth_mhz = int(5.0 * (1 - guard_band_fraction) / 0.18) * 0.18  # MHz
            ue_body_loss = 4.0  # dB
            ue_antenna_gain = -3.0  # dBi
            wavelen = 3e8 / (imt_freq_mhz * 1e6)  # m
            imt_dl_pfd_aggregated = imt_dl_interf_power_samples - ue_antenna_gain \
                - 10 * np.log10(wavelen**2 / (4 * np.pi)) + ue_body_loss - 10 * np.log10(ue_bandwidth_mhz)
            # Store as SampleList in Result object - NOTE: imt_dl_pfd_aggregated attribute does not exist in the 
            # Results class
            res.imt_dl_pfd_aggregated = SampleList(imt_dl_pfd_aggregated)

    post_processor.RESULT_FIELDNAME_TO_PLOT_INFO.update({
        "imt_dl_pfd_aggregated": {
            "x_label": "PFD [dBW/m²/MHz]",
            "title": "[IMT] DL Aggregated PFD",
        },
    })
    # for res in cdf_results:
    #     print("res.output_directory", res.output_directory)

    # for res in ccdf_results:
    #     # converting dBm to dB
    #     # TODO: update this after fixing unit problems at the SHARC simulator
    #     res.system_dl_interf_power_per_mhz = SampleList(np.array(
    #             res.system_dl_interf_power_per_mhz
    #         ) - 30)

    for (
        imt_ue_type,
        _,  # ignore imt frequency from combination
        beam_elev,
        exclusion_margin_km,
        pwr_boff,
        lf,
        prop,
    ) in product(*scenario_params):
        # Get the filename pattern
        specific = get_specific_pattern(
            imt_ue_type, imt_id, imt_frequency_mhz, mss_d2d_id, beam_elev, exclusion_margin_km, pwr_boff, lf, use_phased_array
        )
        post_processor\
            .add_plot_legend_pattern(
                dir_name_contains=specific,
                legend=get_readable(
                    imt_ue_type,
                    imt_id,
                    mss_d2d_id,
                    beam_elev,
                    exclusion_margin_km,
                    pwr_boff,
                    lf)
            )
    # ^: typing.List[Results]

    plots = post_processor.generate_ccdf_plots_from_results(
        ccdf_results,
        cutoff_percentage=cutoff_percentage,
        n_bins=200,
    )

    post_processor.add_plots(plots)

    plots = post_processor.generate_cdf_plots_from_results(
        cdf_results,
        n_bins=200,

    )

    post_processor.add_plots(plots)

    # Add protection criteria line
    imt_dl_inr_plot = post_processor.get_plot_by_results_attribute_name(
        "imt_dl_inr", plot_type="ccdf")
    if imt_dl_inr_plot is not None:
        imt_dl_inr_plot.add_hline(
            y=0.001,
            line_dash="dash",
            line_color="red",
            annotation_text="Protection Criterion (INR = -6 dB, 1 - p = 99,9%)",
            annotation_position="top left",
            annotation_font_size=14,
        )
        imt_dl_inr_plot.add_vline(
            x=-6,
            line_dash="dash",
            line_color="red",
        )
        imt_dl_inr_plot.update_yaxes(
            title_text="CCDF",
        )
        imt_dl_inr_plot.update_xaxes(
            title_text="INR [dB]",
        )

    # Customize PFD plots
    for pfd_attr in ['imt_dl_pfd_aggregated-ccdf', 'imt_dl_pfd']:
        imt_dl_pfd_external_plot = post_processor.get_plot_by_results_attribute_name(
            pfd_attr, plot_type="ccdf")
        if imt_dl_pfd_external_plot is not None:
            pfd_limit = -114.93  # dBW/m2.MHz
            imt_dl_pfd_external_plot.add_vline(
                x=pfd_limit,
                line_dash="dash",
                line_color="red",
                annotation_text=f"PFD Limit ({pfd_limit} dBW/m²/MHz)",
                annotation_position="top left",
                annotation_font_size=14,
            )
            imt_dl_pfd_external_plot.update_yaxes(
                title_text="CCDF",
            )
            imt_dl_pfd_external_plot.update_xaxes(
                title_text="PFD [dBW/m²/MHz]",
            )
            imt_dl_pfd_external_plot.update_layout(
                legend=dict(
                    font=dict(size=14),
                    x=-0.2,
                    y=-0.0,
                    # xanchor='left',
                    orientation='h',
                    xanchor='left',
                    yanchor='bottom',
                    bgcolor='rgba(255,255,255,0.7)',
                    bordercolor='black',
                    borderwidth=1
                )
            )

    HTMLS_DIR = campaign_ouput_dir / "htmls"
    HTMLS_DIR.mkdir(exist_ok=True)
    print(f"Saving plots in {HTMLS_DIR}")
    # Adding PFD aggregated to attributes to plot
    attributes_to_plot.append(("imt_dl_pfd_aggregated", "ccdf"))
    for attr, plot_type in attributes_to_plot:
        file = HTMLS_DIR / f"{attr}-{plot_type}_{imt_frequency_mhz}mhz_{"array" if use_phased_array else "fixed"}_pattern.html"
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=plot_type)
        if plot is None:
            print("Skipping", attr, plot_type)
            continue
        # Add plot outline and increase font size
        current_title = plot.layout.title.text
        plot.update_layout(
            title={'text': current_title + f" - {imt_frequency_mhz}MHz - {"array" if use_phased_array else "fixed"} antenna pattern"}
        )
        plot.update_xaxes(
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            gridcolor="#DCDCDC",
            gridwidth=1.5,
            title_font=dict(size=16),
            tickfont=dict(size=16),
        )
        plot.update_yaxes(
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            gridcolor="#DCDCDC",
            gridwidth=1.5
        )
        plot.update_layout(
            xaxis_title_font=dict(size=24),
            yaxis_title_font=dict(size=24),
            template="plotly_white"
        )
        plot.update_layout(
            legend=dict(
                font=dict(size=14),
                x=0.01,
                y=-2.0,
                # xanchor='left',
                orientation='h',
                xanchor='left',
                yanchor='bottom',
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor='black',
                borderwidth=1
            )
        )
        plot.update_layout(width=1400, height=2000)
        # Set color for each beam elevation
        beam_elev_colors = {
            20: "#1f77b4",
            30: "#ff7f0e",
            45: "#2ca02c",
            70: "#d62728",
            80: "#9467bd",
        }

        for trace in plot.data:
            if trace.name:
                match = re.search(r".*Elev\. = (\d+).*", trace.name)
                if match:
                    beam_elev = int(match.group(1))
                    if beam_elev in beam_elev_colors:
                        trace.line.color = beam_elev_colors[beam_elev]

        # Set marker for each load factor
        load_factor_markers = {
            "20": "circle",
            "50": "square",
        }

        for trace in plot.data:
            if trace.name:
                match = re.search(r".*Load Factor = ([\d.]+)%", trace.name)
                if match:
                    load_factor = match.group(1)
                    if load_factor == "50":
                        trace.line.width = 4
                    else:
                        trace.line.width = 2

        plot.write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)
        # plot.show()

