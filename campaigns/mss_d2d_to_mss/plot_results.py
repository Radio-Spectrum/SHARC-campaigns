from itertools import product
import numpy as np
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

from campaigns.mss_d2d_to_mss.constants import (
    CAMPAIGN_DIR, MSS_ES_TO_READABLE, IMT_MSS_DC_ID_TO_READABLE,
    IMT_MSS_DC_IDS, MSS_DC_LOAD_FACTORS, SINGLE_ES_MSS_IDS,
    get_specific_pattern,
)

auto_open = False

post_processor = PostProcessor()

# Samples to plot CCDF from

attributes_to_plot = [
    ("imt_system_antenna_gain", "cdf"),
    ("imt_system_path_loss", "cdf"),
    ("system_imt_antenna_gain", "cdf"),
    ("system_inr", "cdf"),
    ("system_inr", "ccdf"),
]

samples_for_ccdf = [attr[0] for attr in attributes_to_plot if attr[1] == "ccdf"]
samples_for_cdf = [attr[0] for attr in attributes_to_plot if attr[1] == "cdf"]

ccdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output",
    # filter_fn=lambda x: "mss_d2d_to_eess" in x,
    only_latest=True,
    only_samples=samples_for_ccdf)

cdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output",
    # filter_fn=lambda x: "mss_d2d_to_eess" in x,
    only_latest=True,
    only_samples=samples_for_cdf)

# for res in cdf_results:
#     print("res.output_directory", res.output_directory)

for res in ccdf_results:
    # converting dBm to dB
    # TODO: update this after fixing unit problems at the SHARC simulator
    res.system_dl_interf_power_per_mhz = SampleList(np.array(
            res.system_dl_interf_power_per_mhz
        ) - 30)

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
    i = 0
    styles = ["solid", "dot", "dash", "dashdot"]
    if "spurious_mask" in results.output_directory:
        i = i + 1
    if "340km" in results.output_directory:
        i = i + 2
    return styles[i]


post_processor.add_results_linestyle_getter(linestyle_getter)

for mss_dc_id, mss_es_id, load_factor in product(
   IMT_MSS_DC_IDS, SINGLE_ES_MSS_IDS , MSS_DC_LOAD_FACTORS
):
    readable_mss = IMT_MSS_DC_ID_TO_READABLE[mss_dc_id]
    readable_sys = MSS_ES_TO_READABLE[mss_es_id]
    readable_load = f"Load = {load_factor * 100}%"
    # IMT-MSS-D2D-DL to EESS
    post_processor\
        .add_plot_legend_pattern(
            dir_name_contains=get_specific_pattern(
                mss_dc_id, mss_es_id, load_factor
            ),
            legend=f"{readable_sys}; {readable_mss}, {readable_load}"
        )
# ^: typing.List[Results]

plots = post_processor.generate_ccdf_plots_from_results(
    ccdf_results
)

post_processor.add_plots(plots)

plots = post_processor.generate_cdf_plots_from_results(
    cdf_results
)

post_processor.add_plots(plots)

system_dl_interf_power_per_mhz = post_processor.get_plot_by_results_attribute_name(
    "system_dl_interf_power_per_mhz", plot_type="ccdf")
if system_dl_interf_power_per_mhz is not None:
    system_dl_interf_power_per_mhz.update_xaxes(
        title_text="dB[W/MHz]",
    )


HTMLS_DIR = CAMPAIGN_DIR / "output" / "htmls"
HTMLS_DIR.mkdir(exist_ok=True)
print(f"Saving plots in {HTMLS_DIR}")
for attr, plot_type in attributes_to_plot:
    file = HTMLS_DIR / f"{attr}-{plot_type}.html"
    plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=plot_type)
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
