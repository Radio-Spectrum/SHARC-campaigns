from itertools import product
import numpy as np
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor
import plotly.graph_objects as go
import re

from campaigns.multiple_mss_dc_to_imt.constants import (
    CAMPAIGN_DIR, PARAMETERS, get_specific_pattern,
    get_readable, CELL_RADIUS_SYS3_KM, CELL_RADIUS_SYS4_KM, IMT_LINKS,
    FREQ_BAND_EDGES_DL_MHZ, MSS_D2D_LOAD_FACTOR, SYS_ID_TO_READABLE, SYS_IDS
)

auto_open = False
do_aggregation_plots = False
# SYS3_EXCL_DIST_TO_FILTER = '20'
# SYS4_EXCL_DIST_TO_FILTER = '30'

# post_processor = PostProcessor()

# for pars in product(*PARAMETERS):
#     # IMT-MSS-D2D-DL to EESS
#     pat = get_specific_pattern(*pars)
#     post_processor\
#         .add_plot_legend_pattern(
#             dir_name_contains=pat,
#             legend=get_readable(*pars)
#         )

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
        (
            "_fr_" in results.output_directory and
            "system-4.2110-2200MHz.690km" in results.output_directory
        )
        or (
            "_fr_" in results.output_directory and
            "system-3.2110-2200MHz.525km" in results.output_directory
        )
    ):
        i = 1
    if (
        (
            "_de_" in results.output_directory and
            "system-3.2110-2200MHz.525km" in results.output_directory
        )
        or (
            "_de_" in results.output_directory and
            "system-4.2110-2200MHz.690km" in results.output_directory
        )
    ):
        i = 0
    return styles[i]


# Samples to plot CCDF from

attributes_to_plot = [
    # ("imt_system_antenna_gain", "cdf"),
    # ("imt_system_path_loss", "cdf"),
    # ("imt_system_path_loss", "ccdf"),
    # ("system_imt_antenna_gain", "cdf"),
    # ("system_imt_antenna_gain", "ccdf"),
    # ("sys_to_imt_coupling_loss", "ccdf"),
    # ("sys_to_imt_coupling_loss", "cdf"),
    # ("imt_dl_inr", "cdf"),
    # ("imt_ul_inr", "cdf"),
    ("imt_dl_inr", "ccdf"),
    ("imt_ul_inr", "ccdf"),
]

samples_for_ccdf = [attr[0] for attr in attributes_to_plot if attr[1] == "ccdf"]
samples_for_cdf = [attr[0] for attr in attributes_to_plot if attr[1] == "cdf"]

# def filter_fn(x):
#     # return "0.5load_" in x
#     # return "0.2load_" in x
#     return "0.1load_" in x

imt_scenarios_str = [
    "-rural-macro-",
    "-suburban-macro-",
    "-urban-macro-",
]

plot_group = [
    IMT_LINKS,
    MSS_D2D_LOAD_FACTOR,
    imt_scenarios_str,
    # FREQ_BAND_EDGES_DL_MHZ,
    SYS_IDS,
    ["de", "fr"]
]


def compatible_patterns(s1, s2):
    a = compatible_patterns_ordered(s1, s2)
    if a is not None:
        return a
    b = compatible_patterns_ordered(s2, s1)
    return b

def compatible_patterns_ordered(s1, s2):
    if "0.1load" in s1:
        rload = "Aggregated; LF = 10%; "
    elif "0.2load" in s1:
        rload = "Aggregated; LF = 20%; "
    elif "0.5load" in s1:
        rload = "Aggregated; LF = 50%; "
    # sys3_name = "system-3.698-960MHz.525km"
    # sys4_name = "system-4.698-960MHz-block2.690km"
    sys3_name = "system-3.2110-2200MHz.525km"
    sys4_name = "system-4.2110-2200MHz.690km"
    if ("_downlink_" in s1) and ("_downlink_" in s2):
        if sys3_name in s1:
            s1 = s1.replace(
                sys3_name, sys4_name
            )
            if "to_imt_de" in s1:
                if s1.replace(
                    "to_imt_de",
                    "to_imt_fr",
                ) == s2:
                    return rload + "DE3 & FR4"
            elif "to_imt_fr" in s1:
                if s1.replace(
                    "to_imt_fr",
                    "to_imt_de",
                ) == s2:
                    return rload + "FR3 & DE4"
    elif ("_uplink_" in s1) and ("_uplink_" in s2):
        # rload + "DE3 & FR4 RURAL"
        # rload + "DE3 & FR4 SUBURBAN"
        # rload + "DE3 & FR4 SUBURBAN"
        # rload + "FR3 & DE4 RURAL"
        # rload + "FR3 & DE4 SUBURBAN"
        # rload + "FR3 & DE4 SUBURBAN"
        if sys3_name in s1:
            s1 = s1.replace(
                sys3_name, sys4_name
            )
            if "to_imt_de" in s1:
                if s1.replace(
                    "to_imt_de",
                    "to_imt_fr",
                ) == s2:
                    if "rural-macro" in s1:
                        return rload + "DE3 & FR4 - Macro Rural"
                    elif "suburban-macro" in s1:
                        return rload + "DE3 & FR4 - Macro Suburban"
                    elif "urban-macro" in s1:
                        return rload + "DE3 & FR4 - Macro Urban"
            elif "to_imt_fr" in s1:
                if s1.replace(
                    "to_imt_fr",
                    "to_imt_de",
                ) == s2:
                    if "rural-macro" in s1:
                        return rload + "FR3 & DE4 - Macro Rural"
                    elif "suburban-macro" in s1:
                        return rload + "FR3 & DE4 - Macro Suburban"
                    elif "urban-macro" in s1:
                        return rload + "FR3 & DE4 - Macro Urban"
    return None

output_dir_pattern = r'.*_(de|fr)_(\d+)exclusion_(0.\d+)load_(uplink|downlink)_(\d+)mhz_(imt.*)_(system-.*km)_.*'


def get_compatible_patterns_regex(s1, s2):
    lf_readable = {
        "0.1": "10",
        "0.2": "20",
        "0.5": "50",
    }
    rload = "Aggregated: "

    s1_matches = re.findall(output_dir_pattern, s1)[0]
    s2_matches = re.findall(output_dir_pattern, s2)[0]
    if not s1_matches or not s2_matches:
        return None

    must_match_idxs = [3, 4, 5]
    num_matches = 0
    for i in must_match_idxs:
        if s1_matches[i] == s2_matches[i]:
            num_matches += 1
    if num_matches == len(must_match_idxs) and \
        s1_matches[0] != s2_matches[0] and \
            s1_matches[6] != s2_matches[6]:
        # there's a match between folder names, just the countries are different
        return rload + f"{s1_matches[0].upper()}{SYS_ID_TO_READABLE[s1_matches[6]][-1:]} + {s2_matches[0].upper()}{SYS_ID_TO_READABLE[s2_matches[6]][-1:]}; LF ={lf_readable[s1_matches[2]]}%; {s1_matches[4]}MHz; Excl. Dist. {s1_matches[1]}km" 
    else:
        return None

for (
    link,
    load,
    imt_scenario,
    # freq,
    sys_id,
    country,
) in product(*plot_group):
    
    post_processor = PostProcessor()

    for pars in product(*PARAMETERS):
        # IMT-MSS-D2D-DL to EESS
        pat = get_specific_pattern(*pars)
        post_processor\
            .add_plot_legend_pattern(
                dir_name_contains=pat,
                legend=get_readable(*pars)
            )
    post_processor.add_results_linestyle_getter(linestyle_getter)

    # sys3_pattern = fr".*_{SYS3_EXCL_DIST_TO_FILTER}exclusion_{load}load_{link}_{freq}mhz_.*{imt_scenario}.*_system-3.*"
    # sys4_pattern = fr".*_{SYS4_EXCL_DIST_TO_FILTER}exclusion_{load}load_{link}_{freq}mhz_.*{imt_scenario}.*_system-4.*"
    # sys3_pattern = fr".*exclusion_{load}load_{link}_{freq}mhz_.*{imt_scenario}.*_system-3.*"
    # sys4_pattern = fr".*exclusion_{load}load_{link}_{freq}mhz_.*{imt_scenario}.*_system-4.*"
    result_pattern = fr".*_{country}_.*exclusion_{load}load_{link}_.*_.*{imt_scenario}.*{sys_id}*"
    # dir_name_regex = f"({sys3_pattern})|({sys4_pattern})"
    # dir_name_regex = f"{sys4_pattern}"
    dir_name_regex = f"{result_pattern}"

    ccdf_results = Results.load_many_from_dir(
        CAMPAIGN_DIR / "output",
        filter_fn=lambda x: re.search(dir_name_regex, x) is not None,
        only_latest=True,
        only_samples=samples_for_ccdf)

    cdf_results = Results.load_many_from_dir(
        CAMPAIGN_DIR / "output",
        filter_fn=lambda x: re.search(dir_name_regex, x) is not None,
        only_latest=True,
        only_samples=samples_for_cdf)

    if len(ccdf_results) == 0:
        print(f"No results found for {load} load, {imt_scenario}, {SYS_ID_TO_READABLE[sys_id]}. Skipping")
        continue

    # for res in cdf_results:
    #     print("res.output_directory", res.output_directory)

    for res in ccdf_results:
        # converting dBm to dB
        # TODO: update this after fixing unit problems at the SHARC simulator
        res.system_dl_interf_power_per_mhz = SampleList(np.array(
                res.system_dl_interf_power_per_mhz
            ) - 30)

    # ^: typing.List[Results]
    plots = post_processor.generate_ccdf_plots_from_results(
        ccdf_results, cutoff_percentage=0.001 / 2
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

    plots_to_save = []
    HTMLS_DIR = CAMPAIGN_DIR / "output" / "htmls"
    HTMLS_DIR.mkdir(exist_ok=True)

    if link == "downlink":
        attr = "imt_dl_inr"
    else:
        attr = "imt_ul_inr"
    fig = post_processor.get_plot_by_results_attribute_name(attr, plot_type="ccdf")
    calculate_percentile_for = [
        # (legend, aggr)
    ]
    if do_aggregation_plots:
        for i in range(len(ccdf_results)):
            for j in range(i+1, len(ccdf_results)):
                r = ccdf_results[i]
                r2 = ccdf_results[j]
                if link in r.output_directory and link in r2.output_directory:
                    legend = get_compatible_patterns_regex(r.output_directory, r2.output_directory)
                    if legend is not None:
                        if fig is None:
                            # getting same formatting that other plots get
                            if not list(post_processor.generate_ccdf_plots_from_results([r])):
                                print(f"empty folder found in {r.output_directory}")
                                continue
                            fig = list(post_processor.generate_ccdf_plots_from_results([r]))[0]
                            fig.data = []
                            plots_to_save.append((HTMLS_DIR / "aggregated.html", fig))
                        inr1 = np.array(getattr(r, attr))
                        inr2 = np.array(getattr(r2, attr))
                        minl = np.minimum(len(inr1), len(inr2))
                        aggregated_inr = 10 * np.log10(
                            10**(inr1[:minl]) / 10 + \
                            10**(inr2[:minl]) / 10
                        )
                        calculate_percentile_for.append((legend, aggregated_inr))
                        x, y = PostProcessor.ccdf_from(aggregated_inr, n_bins=None)
                        linestyle = linestyle_getter(r2)
                        from plotly.colors import DEFAULT_PLOTLY_COLORS

                        color_i = 0
                        while True:
                            if color_i >= len(DEFAULT_PLOTLY_COLORS):
                                color_i = 0
                                break
                            some_has = False
                            for obj in fig.data:
                                if obj.line.dash == linestyle and obj.line.color == DEFAULT_PLOTLY_COLORS[color_i]:
                                    some_has = True
                                    break
                            if not some_has:
                                break
                            else:
                                color_i += 1
            
                        fig.add_trace(
                            go.Scatter(
                                x=x,
                                y=y,
                                mode="lines",
                                name=f"{legend}",
                                line=dict(color=DEFAULT_PLOTLY_COLORS[color_i], dash=linestyle)
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
        file = HTMLS_DIR / f"{attr}-{country}-{sys_id}-{load}load{imt_scenario}{plot_type}.html"
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=plot_type)
        if plot is None:
            print("Skipping", attr, plot_type)
            continue
        plots_to_save.append((file, plot))

    protection_criteria = -6
    perc_time = 0.001

    for attr in ["imt_dl_inr", "imt_ul_inr"]:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type="ccdf")
        if plot is not None:
            plot.update_layout(title_text=f"CCDF of IMT-UL {imt_scenario[1:-1].upper().replace("-", " ")}")
            plot.add_vline(
                protection_criteria,
                line_dash="dash", annotation=dict(
                    text="-6dB Protection criteria",
                    font=dict(size=20),
                    xref="x",
                    yref="paper",
                    x=protection_criteria + 0.2,  # Offset for visibility
                    y=0.85
                )
            )
            plot.add_hline(perc_time, line_dash="dash", annotation=dict(
                text="Time Percentage: " + str(perc_time * 100) + "%",
                xref="x", yref="y",
                x=protection_criteria + 0.5, y=perc_time + 0.01,
                font=dict(size=12, color="blue")
            ))
            plot.update_xaxes(
                title_text="I/N"
            )
        else:
            print(f"Warning: No plot found for attribute '{attr}'")

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
                y=-0.8,
                # xanchor='left',
                orientation='h',
                xanchor='left',
                yanchor='bottom',
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor='black',
                borderwidth=1
            )
        )
        plot.update_layout(
            width=1000,
            height=1400,
            margin=dict(
                l=50,  # left margin
                r=50,  # right margin
                b=100,  # bottom margin
                t=100,  # top margin
                pad=4  # padding between plot area and axis labels
            )
        )
        plot.write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)
        # plot.show()

    percentiles = [(1 - perc_time)*100]
    # percentiles = [99.9]
    for res in ccdf_results:
        name = post_processor.get_results_possible_legends(res)[0]['legend']
        inr_values = res.imt_dl_inr
        if inr_values is None or len(inr_values) == 0:
            print("Skipped one result for percentile calc")
            continue
        calculate_percentile_for.append((name, inr_values))

    percentile_file = HTMLS_DIR / f"percentiles-{link}-{SYS_ID_TO_READABLE[sys_id]}-{load}load{imt_scenario[:-1]}.txt"
    with open(percentile_file, 'w') as f:
        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write("Percentiles\n")
        for name, inr_values in calculate_percentile_for:
            f.write(f"{name}\n")
            res = np.percentile(inr_values, percentiles, method='inverted_cdf')
            exceedance = res - protection_criteria
            colsize = 6
            f.write(f"\t{'Percentile':<10} ; {'Exceeded':<10}\n")
            for i in range(len(percentiles)):
                f.write(f"\t{percentiles[i]:<10} ; ")
                f.write(f"{round(exceedance[i], 5):<10}\n")
