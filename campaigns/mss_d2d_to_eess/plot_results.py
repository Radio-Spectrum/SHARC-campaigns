import os
from sharc.results import Results
from sharc.post_processor import PostProcessor

from campaigns.mss_d2d_to_eess.constants import CAMPAIGN_DIR, SYS_ID_TO_READABLE, get_specific_pattern, MSS_ID_TO_READABLE

auto_open = True

post_processor = PostProcessor()

# Samples to plot CCDF from
samples_for_ccdf = [
    "system_dl_interf_power_per_mhz"
]

samples_for_cdf = [
    "imt_system_antenna_gain",
    "imt_system_path_loss",
    "system_dl_interf_power",
    "system_imt_antenna_gain",
    "system_inr", "ccdf"
]

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

for mss_dc in [
    "imt.2110-2200MHz.mss-dc.system3-525km",
    "imt.2110-2200MHz.mss-dc.system3-340km",
]:
    readable_mss = MSS_ID_TO_READABLE[mss_dc]
    for sys_name in [
        "eess.2200-2290MHz.system-B",
        "eess.2200-2290MHz.system-D",
    ]:
        readable_sys = SYS_ID_TO_READABLE[sys_name]
        for load in [
            0.2,
            0.5,
            1
        ]:
            readable_load = f"Load = {load * 100}%"
            for mask in [
                "mss",
                "spurious",
            ]:
                readable_mask = {
                    "mss": "@2197.5",
                    "spurious": "@2167.5",
                }[mask]
                for elev in [5, 30, 60, 90, "uniform"]:
                    if elev == "uniform":
                        readable_elev = "Elev = Unif. Dist."
                    else:
                        readable_elev = f"Elev = {elev}º"
                    # IMT-MSS-D2D-DL to EESS
                    post_processor\
                        .add_plot_legend_pattern(
                            dir_name_contains=get_specific_pattern(
                                elev, sys_name, mss_dc, mask, load
                            ),
                            legend=f"{readable_sys}; {readable_mss}, {readable_load}, {readable_mask}"
                            # legend=f"{readable_sys}, {readable_elev}; {readable_mss}, {readable_load}, {readable_mask}"
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

# plots = post_processor.generate_ccdf_plots_from_results(
#     many_results
# )

# post_processor.add_plots(plots)

# Add a protection criteria line:
protection_criteria = -154.0  # dBm/MHz
perc_time = 0.01
system_dl_interf_power_per_mhz = post_processor.get_plot_by_results_attribute_name(
    "system_dl_interf_power_per_mhz", plot_type="ccdf")
system_dl_interf_power_per_mhz.add_vline(
    protection_criteria,
    line_dash="dash",
    annotation=dict(
        text="Protection Criteria: " +
        str(protection_criteria) +
        " dB[W/MHz]",
        xref="x",
        yref="y",
        x=protection_criteria +
        0.5,
        y=0.8,
        font=dict(
            size=12,
             color="red")))
system_dl_interf_power_per_mhz.add_hline(perc_time, line_dash="dash", annotation=dict(
    text="Time Percentage: " + str(perc_time * 100) + "%",
    xref="x", yref="y",
    x=protection_criteria + 0.5, y=perc_time + 0.01,
    font=dict(size=12, color="blue")
))


attributes_to_plot = [
    ("imt_system_antenna_gain", "cdf"),
    ("imt_system_path_loss", "cdf"),
    ("system_dl_interf_power", "cdf"),
    ("system_dl_interf_power_per_mhz", "ccdf"),
    ("system_imt_antenna_gain", "cdf"),
    ("system_inr", "cdf"),
]

HTMLS_DIR = CAMPAIGN_DIR / "output" / "htmls"
HTMLS_DIR.mkdir(exist_ok=True)
print(f"Saving plots in {HTMLS_DIR}")
for attr, plot_type in attributes_to_plot:
    file = HTMLS_DIR / f"{attr}.html"
    post_processor\
        .get_plot_by_results_attribute_name(attr, plot_type=plot_type)\
        .write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)

