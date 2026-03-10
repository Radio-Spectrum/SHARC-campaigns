import numpy as np
from sharc.results import Results, SampleList
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
    # filter_fn=lambda x: "_0.00" in x,
    only_latest=True,
    only_samples=samples_for_ccdf)

cdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output",
    # filter_fn=lambda x: "_0.00" in x,
    only_latest=True,
    only_samples=samples_for_cdf)

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
    if "0.0" in results.output_directory:
        i = i
    elif "24." in results.output_directory:
        i = i + 1
    elif "48." in results.output_directory:
        i = i + 2
    return styles[i]


post_processor.add_results_linestyle_getter(linestyle_getter)

for imt_mss_dc_id in [
    # "imt.2110-2200MHz.mss-dc.system3-525km",
    # "imt.2110-2200MHz.mss-dc.system3-340km",
    "imt.1427-2690MHz.mss-dc.system4-690km",
]:
    readable_mss = MSS_ID_TO_READABLE[imt_mss_dc_id]
    for eess_sys_id in [
        "eess.2200-2290MHz.system-B",
        "eess.2200-2290MHz.system-D",
    ]:
        readable_sys = SYS_ID_TO_READABLE[eess_sys_id]
        for excl_radius_km in [
            0.0001,
            24.,
            48.
        ]:
            for load in [
                0.2,
                0.5,
            ]:
                for freq_offset in [
                    0,
                    5,
                ]:
                    readable_load = f"Load = {load * 100}%"

                    readable_offset = {
                        0: "first_adj",
                        5: "second_adj",
                    }[freq_offset]
                    # IMT-MSS-D2D-DL to EESS
                    # hack to cope with almost zero excl radius
                    excl_readius_readable = "0.0km" if excl_radius_km < 0.1 else f"{excl_radius_km:.2f}km"
                    post_processor\
                        .add_plot_legend_pattern(
                            dir_name_contains=get_specific_pattern(
                                "uniform", eess_sys_id, imt_mss_dc_id, readable_offset, excl_radius_km, load
                            ),
                            legend=f"{readable_sys}; {readable_mss}, {readable_load}, {readable_offset}, {excl_readius_readable}"
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
system_dl_interf_power_per_mhz.update_xaxes(
    title_text="dB[W/MHz]",
)


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
            y=-1.0,
            # xanchor='left',
            orientation='h',
            xanchor='left',
            yanchor='bottom',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='black',
            borderwidth=1
        ),
        width=800,
        height=1400
    )

    plot.write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)

