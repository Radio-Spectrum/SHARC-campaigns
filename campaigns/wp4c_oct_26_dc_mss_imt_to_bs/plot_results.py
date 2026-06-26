from itertools import product
import numpy as np
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

from campaigns.wp4c_oct_26_dc_mss_imt_to_bs.constants import (
    CAMPAIGN_DIR,
    BS_IDS,
    BS_TO_READABLE,
    BS_CHANNELS,
    IMT_MSS_DC_ID_TO_READABLE,
    IMT_MSS_DC_IDS,
    MSS_DC_LOAD_FACTORS,
    BS_REPECTION_TYPE,
    get_specific_pattern,
)

auto_open = False

# Attributes to plot (CDF + CCDF)
attributes_to_plot = [
    ("imt_system_antenna_gain", "cdf"),
    ("imt_system_path_loss", "cdf"),
    ("system_imt_antenna_gain", "cdf"),
    ("system_inr", "cdf"),
    ("system_inr", "ccdf"),
]

samples_for_ccdf = [attr[0]
                    for attr in attributes_to_plot if attr[1] == "ccdf"]
samples_for_cdf = [attr[0] for attr in attributes_to_plot if attr[1] == "cdf"]

# # Load CCDF results
# ccdf_results = Results.load_many_from_dir(
#     CAMPAIGN_DIR / "output",
#     only_latest=True,
#     only_samples=samples_for_ccdf
# )

# # Load CDF results
# cdf_results = Results.load_many_from_dir(
#     CAMPAIGN_DIR / "output",
#     only_latest=True,
#     only_samples=samples_for_cdf
# )

# results = Results.load_many_from_dir(
#     OUTPUT_ROOT_FOLDER,
#     only_latest=True,
#     filter_fn=lambda s: any(mss_id in str(s) and adj_ch_readable in str(s) for mss_id in args.mss_ids),
#     only_samples=attributes_to_plot
# )

# # --- Unit fixes ---
# for res in ccdf_results:
#     # Convert dBm → dB[W] for power
#     if hasattr(res, "system_dl_interf_power_per_mhz"):
#         res.system_dl_interf_power_per_mhz = SampleList(
#             np.array(res.system_dl_interf_power_per_mhz) - 30
#         )

#     # Convert INR to dB (dimensionless) if simulator exported it like dBm
#     if hasattr(res, "system_inr"):
#         arr = np.array(res.system_inr)
#         # INR should be around -20 .. +20 dB normally
#         if arr.max() > 50:  # looks like dBm offset
#             res.system_inr = SampleList(arr - 30)


def linestyle_getter(results):
    """Choose line style based on folder name."""
    i = -1
    styles = ["solid", "dot", "dash", "dashdot"]
    if "525km" in results.output_directory:
        i += 1
    elif "340km" in results.output_directory:
        i += 2
    elif "690km" in results.output_directory:
        i += 3
    else:
        return "solid"
    return styles[i]


for bs_reception_type in BS_REPECTION_TYPE:

    # Load CCDF results
    ccdf_results = Results.load_many_from_dir(
        CAMPAIGN_DIR / "output",
        only_latest=True,
        only_samples=samples_for_ccdf,
        filter_fn=lambda s: bs_reception_type in str(s),
    )

    # Load CDF results
    cdf_results = Results.load_many_from_dir(
        CAMPAIGN_DIR / "output",
        only_latest=True,
        only_samples=samples_for_cdf,
        filter_fn=lambda s: bs_reception_type in str(s),
    )

    post_processor = PostProcessor()
    post_processor.add_results_linestyle_getter(linestyle_getter)

    # Legend labels
    for imt_id, bs_id, load_factor, bs_channel in product(
        IMT_MSS_DC_IDS, BS_IDS, MSS_DC_LOAD_FACTORS, BS_CHANNELS.keys()
    ):
        readable_bs = BS_TO_READABLE[bs_id]
        readable_dc_mss = IMT_MSS_DC_ID_TO_READABLE[imt_id]
        readable_load = f"Load = {load_factor * 100}%"
        post_processor.add_plot_legend_pattern(
            dir_name_contains=get_specific_pattern(
                imt_id, bs_id, load_factor, bs_channel, bs_reception_type),
            legend=f"{readable_dc_mss}; {readable_bs}, CH={bs_channel}, {bs_reception_type}, {readable_load}"
        )

    # Generate plots
    plots = post_processor.generate_ccdf_plots_from_results(ccdf_results, n_bins=200, cutoff_percentage=1e-5)
    post_processor.add_plots(plots)

    plots = post_processor.generate_cdf_plots_from_results(cdf_results)
    post_processor.add_plots(plots)

    system_dl_interf_power_per_mhz = post_processor.get_plot_by_results_attribute_name(
        "system_dl_interf_power_per_mhz", plot_type="ccdf"
    )
    if system_dl_interf_power_per_mhz is not None:
        system_dl_interf_power_per_mhz.update_xaxes(
            title_text="dB[W/MHz]",
        )

    system_inr_plot = post_processor.get_plot_by_results_attribute_name(
        "system_inr", plot_type="ccdf"
    )
    if system_inr_plot is not None:
        system_inr_plot.update_xaxes(
            title_text="INR [dB]",
        )

    HTMLS_DIR = CAMPAIGN_DIR / "output" / "htmls"
    HTMLS_DIR.mkdir(exist_ok=True)
    print(f"Saving plots in {HTMLS_DIR}")

    for attr, plot_type in attributes_to_plot:
        file = HTMLS_DIR / f"{attr}-{plot_type}-{bs_reception_type}.html"
        plot = post_processor.get_plot_by_results_attribute_name(
            attr, plot_type=plot_type)
        if plot is None:
            continue

        if attr == "system_inr":
            plot.add_vline(x=-10, line_dash="dot", line_color="red", annotation_text="-10dB", annotation_position="bottom right")
            # plot.add_vline(x=-12.2, line_dash="dot", line_color="gray", annotation_text="-12.2dB", annotation_position="top right")
            # plot.add_hline(y=0.001, line_dash="dot", line_color="gray", annotation_text="0.1%", annotation_position="left")
            # plot.add_hline(y=0.2, line_dash="dot", line_color="gray", annotation_text="20%", annotation_position="left")

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
                orientation='h',
                xanchor='left',
                yanchor='bottom',
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor='black',
                borderwidth=1
            )
        )

        plot.write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)
