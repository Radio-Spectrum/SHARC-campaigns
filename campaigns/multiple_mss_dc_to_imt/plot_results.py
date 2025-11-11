from itertools import product
import numpy as np
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor
import plotly.graph_objects as go

from campaigns.multiple_mss_dc_to_imt.constants import (
    CAMPAIGN_DIR, PARAMETERS, get_specific_pattern,
    get_readable, CELL_RADIUS_SYS3_KM, CELL_RADIUS_SYS4_KM,
)

auto_open = False

post_processor = PostProcessor()

# Samples to plot CCDF from

attributes_to_plot = [
    # ("imt_system_antenna_gain", "cdf"),
    # ("imt_system_path_loss", "cdf"),
    # ("system_imt_antenna_gain", "cdf"),
    # ("imt_dl_inr", "cdf"),
    # ("imt_ul_inr", "cdf"),
    ("imt_dl_inr", "ccdf"),
    # ("imt_ul_inr", "ccdf"),
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
    i = 3
    styles = ["solid", "dot", "dash", "dashdot"]
    if (
        f"_br_{CELL_RADIUS_SYS3_KM}exclusion" in results.output_directory
        or f"_ar_{CELL_RADIUS_SYS4_KM}exclusion" in results.output_directory
    ):
        i = 1
    if (
        f"_ar_{CELL_RADIUS_SYS3_KM}exclusion" in results.output_directory
        or f"_br_{CELL_RADIUS_SYS4_KM}exclusion" in results.output_directory
    ):
        i = 0
    return styles[i]


post_processor.add_results_linestyle_getter(linestyle_getter)

for pars in product(*PARAMETERS):
    # IMT-MSS-D2D-DL to EESS
    pat = get_specific_pattern(*pars)
    post_processor\
        .add_plot_legend_pattern(
            dir_name_contains=pat,
            legend=get_readable(*pars)
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

def compatible_patterns(s1, s2):
    a = compatible_patterns_ordered(s1, s2)
    if a is not None:
        return a
    b = compatible_patterns_ordered(s2, s1)
    return b

def compatible_patterns_ordered(s1, s2):
    if "0.1load" in s1:
        rload = "LF = 10%; "
    elif "0.2load" in s1:
        rload = "LF = 20%; "
    sys3_name = "system-3.698-960MHz.525km"
    sys4_name = "system-4.698-960MHz-block2.690km"
    # sys3_name = "system-3.2110-2200MHz.525km"
    # sys4_name = "system-4.2110-2200MHz.690km"
    if sys3_name in s1:
        s1 = s1.replace(
            sys3_name, sys4_name
        ).replace(
            "39.684", "24.105"
        )
        if "to_imt_br" in s1:
            if s1.replace(
                "to_imt_br",
                "to_imt_ar",
            ) == s2:
                return rload + "BR3 & AR4"
        elif "to_imt_ar" in s1:
            if s1.replace(
                "to_imt_ar",
                "to_imt_br",
            ) == s2:
                return rload + "AR3 & BR4"
    return None

plots_to_save = []
HTMLS_DIR = CAMPAIGN_DIR / "output" / "htmls"
HTMLS_DIR.mkdir(exist_ok=True)

fig = post_processor.get_plot_by_results_attribute_name("imt_dl_inr", plot_type="ccdf")
aggregated_res = [
    # (legend, aggr)
]
for i in range(len(ccdf_results)):
    for j in range(i+1, len(ccdf_results)):
        r = ccdf_results[i]
        r2 = ccdf_results[j]
        legend = compatible_patterns(r.output_directory, r2.output_directory)
        if legend is not None:
            if fig is None:
                # getting same formatting that other plots get
                fig = list(post_processor.generate_ccdf_plots_from_results([r]))[0]
                fig.data = []
                plots_to_save.append((HTMLS_DIR / "aggregated.html", fig))
            aggregated_inr = 10 * np.log10(
                10**(np.array(r.imt_dl_inr)/10)
                + 10**(np.array(r2.imt_dl_inr)/10)
            )
            aggregated_res.append((legend, aggregated_inr))
            x, y = PostProcessor.ccdf_from(aggregated_inr, n_bins=None)
            linestyle = linestyle_getter(r2)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name=f"Aggregated {legend}",
                    line=dict(dash=linestyle)
                ),
            )
            # print()
            # print("########################")
            # print(plot)
            # print("r.output_directory", r.output_directory)
            # print("r2.output_directory", r2.output_directory)
            # print("c", c)


print(f"Saving plots in {HTMLS_DIR}")
for attr, plot_type in attributes_to_plot:
    file = HTMLS_DIR / f"{attr}-{plot_type}.html"
    plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=plot_type)
    if plot is None:
        print("Skipping", attr, plot_type)
        continue
    plots_to_save.append((file, plot))

for file, plot in plots_to_save:
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

percentiles = [0.99]
print()
print("=" * 60)
print("Percentiles")
for res in ccdf_results:
    name = post_processor.get_results_possible_legends(res)[0]['legend']
    inr_values = res.imt_dl_inr
    if inr_values is None or len(inr_values) == 0:
        print("Skipped one")
        continue
    print(f"{name}")
    res = np.percentile(inr_values, percentiles, method='inverted_cdf')
    print("\tpercentiles", percentiles)
    print("\tres", res)

print()
print("=" * 60)
print("Aggregated percentiles")
for name, inr_values in aggregated_res:
    print(f"{name}")
    res = np.percentile(inr_values, percentiles, method='inverted_cdf')
    print("\tpercentiles", percentiles)
    print("\tres", res)
