from itertools import product
import argparse
import re as re
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

from campaigns.ast_mss_d2d_to_imt_cpe.constants import (
    CAMPAIGN_DIR,
    IMT_UE_TYPE,
    MSS_D2D_LOAD_FACTOR,
    get_specific_pattern,
    get_readable
)

# output_ast_mss_d2d_to_imt_cpe_24exclusion_0.2load_imt-cpe_imt.upto-1GHz.single-bs.urban-macro-bs_system-4.698-960MHz-block2.690km_2025-11-10_01
output_dir_pattern = re.compile(
    r".*/output_ast_mss_d2d_to_imt_cpe_(\d+)exclusion_(\d+\.\d+)load_imt-(cpe|ue)_"
)

parser = argparse.ArgumentParser(description='Generate simulation plots')
parser.add_argument('--band_mhz', type=int, choices=[700, 2100], default=700,
                    help='Frequency band in MHz (700 or 2100)')
parser.add_argument('--auto_open', action='store_true', default=False,
                    help='Open the generated HTML plots automatically')

args = parser.parse_args()
auto_open = args.auto_open
band_mhz = args.band_mhz

# Band specific settings
imt_bandwidth_mhz = 5.0  # MHz
if band_mhz == 700:
    print("Generating plots for 700 MHz band...")
    output_dir_regex = "imt.upto-1GHz.single-bs.urban-macro-bs.*"
    imt_id = "imt.upto-1GHz.single-bs.urban-macro-bs"
    mss_id = "system-4.698-960MHz-block2.690km"
    exclusion_margins_km = [24, 30, 36, 40]
else:
    print("Generating plots for 2100 MHz band...")
    output_dir_regex = "1-3GHz.single-bs.aas-macro-bs.*"
    imt_id = "imt.1-3GHz.single-bs.aas-macro-bs"
    mss_id = "system-4.2110-2200MHz.690km"
    exclusion_margins_km = [12, 24, 48]

output_dir = f"output_{band_mhz}"
scenario_params = [
    IMT_UE_TYPE,
    [imt_id],
    [mss_id],
    MSS_D2D_LOAD_FACTOR,
    exclusion_margins_km,
]

post_processor = PostProcessor()

# Samples to plot CCDF from
attributes_to_plot = [
    # ("imt_system_antenna_gain", "cdf"),
    # ("imt_system_path_loss", "cdf"),
    ("system_imt_antenna_gain", "cdf"),
    # ("imt_dl_inr", "cdf"),
    # ("imt_ul_inr", "cdf"),
    ("imt_dl_inr", "ccdf"),
    # ("imt_ul_inr", "ccdf"),
]

samples_for_ccdf = [attr[0] for attr in attributes_to_plot if attr[1] == "ccdf"]
samples_for_cdf = [attr[0] for attr in attributes_to_plot if attr[1] == "cdf"]

campaign_ouput_dir = CAMPAIGN_DIR / output_dir
print("Getting results from", campaign_ouput_dir)
ccdf_results = Results.load_many_from_dir(
    campaign_ouput_dir,
    # filter_fn=lambda x: "mss_d2d_to_eess" in x,
    filter_fn=re.compile(output_dir_regex).search,
    only_latest=True,
    only_samples=samples_for_ccdf)

cdf_results = Results.load_many_from_dir(
    campaign_ouput_dir,
    # filter_fn=lambda x: "mss_d2d_to_eess" in x,
    filter_fn=re.compile(output_dir_regex).search,
    only_latest=True,
    only_samples=samples_for_cdf)

# for res in cdf_results:
#     print("res.output_directory", res.output_directory)

# for res in ccdf_results:
#     # converting dBm to dB
#     # TODO: update this after fixing unit problems at the SHARC simulator
#     res.system_dl_interf_power_per_mhz = SampleList(np.array(
#             res.system_dl_interf_power_per_mhz
#         ) - 30)

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

    exclusion_dist, lf, ue_type = match.groups()
    i = 3
    styles = ["solid", "dot", "dash", "dashdot"]
    if band_mhz == 700:
        if exclusion_dist in ["24"]:
            i = 0
        if exclusion_dist in ["48"]:
            i = 1
        if exclusion_dist in ["72"]:
            i = 2
    else:
        if exclusion_dist in ["12"]:
            i = 0
        if exclusion_dist in ["24"]:
            i = 1
        if exclusion_dist in ["36"]:
            i = 2
    return styles[i]


post_processor.add_results_linestyle_getter(linestyle_getter)

for pars in product(*scenario_params):
    pat = get_specific_pattern(*pars)
    post_processor\
        .add_plot_legend_pattern(
            dir_name_contains=pat,
            legend=get_readable(*pars)
        )
# ^: typing.List[Results]

plots = post_processor.generate_ccdf_plots_from_results(
    ccdf_results,
    cutoff_percentage=0.0005,
    n_bins=200,
)

post_processor.add_plots(plots)

plots = post_processor.generate_cdf_plots_from_results(
    cdf_results,
    n_bins=200,

)

post_processor.add_plots(plots)

# system_dl_interf_power_per_mhz = post_processor.get_plot_by_results_attribute_name(
#     "system_dl_interf_power_per_mhz", plot_type="ccdf")
# if system_dl_interf_power_per_mhz is not None:
#     system_dl_interf_power_per_mhz.update_xaxes(
#         title_text="dB[W/MHz]",
#     )

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


HTMLS_DIR = campaign_ouput_dir / "htmls"
HTMLS_DIR.mkdir(exist_ok=True)
print(f"Saving plots in {HTMLS_DIR}")
for attr, plot_type in attributes_to_plot:
    file = HTMLS_DIR / f"{attr}-{plot_type}.html"
    plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=plot_type)
    if plot is None:
        print("Skipping", attr, plot_type)
        continue
    # Add plot outline and increase font size
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
            x=0.2,
            y=-0.5,
            # xanchor='left',
            orientation='h',
            xanchor='left',
            yanchor='bottom',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='black',
            borderwidth=1
        )
    )
    plot.write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)
    # plot.show()

