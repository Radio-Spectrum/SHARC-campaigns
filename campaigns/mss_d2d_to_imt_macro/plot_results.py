"""Script to process and plot results for MSS D2D to IMT cross-border campaign."""
from itertools import product
import pandas as pd
import re
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from sharc.results import Results
from sharc.post_processor import PostProcessor
from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.mss_d2d_to_imt_macro.generate_params import (
    cmd_line_parser,
    get_specific_pattern,
    IMT_IDS,
    IMT_MSS_DC_ID_TO_READABLE,
    DC_MSS_LOAD_FACTORS,
    LINKS,
    DC_MSS_IDS,
    BAND_TO_DC_MSS_ID_MAP,
    POWER_BACKOFF_VALUES
)
from campaigns.mss_d2d_to_imt_macro.run import CAMPAIGN_STR, CAMPAIGN_DIR, get_output_dir_start, INPUTS_DIR
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

OUTPUT_ROOT_FOLDER = CAMPAIGN_DIR / "output"

OUTPUT_FOLDER_REGEX = r"output_mss_d2d_to_imt_macro_(\d+\.\d+)km_(\d+\.\d+)load_([ud]l)_"


def linestyle_getter(result: Results):
    """
    Returns a line style string based on the prefix found in the result's output directory.
    """
    dirname = result.output_directory

    if "15backoff" in dirname:
        return "dot"
    elif "10backoff" in dirname:
        return "dash"
    elif "0backoff" in dirname:
        return "solid"
    else:
        return "solid"

IMT_ID_TO_READABLE = {
    "imt.1-3GHz.macrocell.aas-urban-macro-bs": "imt_macro_urban_1-3GHz",
    "imt.1-3GHz.macrocell.aas-suburban-macro-bs": "imt_macro_suburban_1-3GHz",
    "imt.1-3GHz.macrocell.aas-rural-macro-bs": "imt_macro_rural_1-3GHz",
}
if __name__ == "__main__":
    post_processor = PostProcessor()
    factory = ParametersFactory()

    parser = cmd_line_parser()
    parser.add_argument(
        "--plot_type",
        type=str,
        choices=["cdf", "ccdf"],
        default="cdf",
        help="Type of plot to generate. Choose 'cdf' or 'ccdf'. Default: 'cdf'"
    )
    args = parser.parse_args()

    for mid in args.mss_ids:
        if mid not in DC_MSS_IDS:
            raise ValueError(f"Invalid MSS ID '{mid}'. Choose from {DC_MSS_IDS}")
        if mid not in BAND_TO_DC_MSS_ID_MAP[args.band_id]:
            raise ValueError(f"MSS ID '{mid}' is not compatible with band {args.band_id}. Choose from {BAND_TO_DC_MSS_ID_MAP[args.band_id]}")

    if args.plot_type not in ["cdf", "ccdf"]:
        raise ValueError("Invalid plot type. Choose 'cdf' or 'ccdf'.")

    campaign_base_dir = str((Path(__file__) / ".." / "..").resolve())

    attributes_to_plot = [
        # "imt_dl_inr",
        "imt_ul_inr",
        "imt_ul_interf_power",
        "imt_ul_snr",
        "imt_ul_sinr",
        "imt_ul_sinr_ext",
        "imt_ul_tput",
        "imt_ul_tput_ext",
        "imt_ul_tx_power",
        "imt_path_loss",
        "imt_ul_intra_interf_power",
        "imt_ul_total_interf_power",
        "imt_system_antenna_gain",
        # "imt_system_path_loss",
        # "system_imt_antenna_gain",
    ]

    adj_ch_readable = "adj" if args.adj else "co"
    html_file_prefix = ""
    for mss_id in args.mss_ids:
        html_file_prefix += f"{mss_id}_"
    html_file_prefix += f"{args.band_id}_"
    html_file_prefix += f"{args.plot_type}_"
    html_file_prefix += f"{adj_ch_readable}"

    results = Results.load_many_from_dir(
        OUTPUT_ROOT_FOLDER,
        only_latest=True,
        filter_fn=lambda s: any(mss_id in str(s) and adj_ch_readable in str(s) for mss_id in args.mss_ids),
        only_samples=attributes_to_plot
    )

    percentile_data = []
    # Generate Legend labels and other information based on all output combinations
    for imt_id, dc_mss_id, load_factor, link, pow_backoff in product(IMT_IDS, args.mss_ids, DC_MSS_LOAD_FACTORS, LINKS, POWER_BACKOFF_VALUES):
        # dc_mss_params = factory.load_from_id(
        #     dc_mss_id
        # )
        dc_mss_params = factory._get_param_as_dict(factory._get_param_dir(dc_mss_id))
        cell_radius = dc_mss_params["mss_d2d"]["cell_radius"]
        min_margin = round(cell_radius / 1e3, 0)
        distances = [min_margin, 2 * min_margin]
        readable_mss = IMT_MSS_DC_ID_TO_READABLE[dc_mss_id]
        readable_load = f"Load = {load_factor * 100}%"
        readable_backoff = f"{int(pow_backoff)}dB Backoff"
        for border in distances:
            # generate legend labels
            postfix_str = get_specific_pattern(
                imt_id,
                dc_mss_id,
                not args.adj,
                args.band_id,
                border,
                load_factor,
                link,
                pow_backoff
            )
            post_processor.add_plot_legend_pattern(
                dir_name_contains=postfix_str,
                legend=f"{readable_mss}, {readable_load}, {readable_backoff}, {border} km margin, IMT-{link.upper()}, {IMT_ID_TO_READABLE[imt_id]}"
            )
            # generate some statistics for INR
            for res in results:
                if postfix_str in res.output_directory:
                    inr_attr = f"{'imt_dl_inr' if link == 'dl' else 'imt_ul_inr'}"
                    if hasattr(res, inr_attr):
                        inr_values = getattr(res, inr_attr)
                        if len(inr_values) == 0:
                            print(f"No {inr_attr} data for {postfix_str}")
                            continue
                        percentile_data.append({
                            "DC-MSS System": readable_mss,
                            "Load": readable_load,
                            "IMT Link": link.upper(),
                            "Margin (km)": border,
                            "Attribute": inr_attr,
                            "p50 (dB)": np.percentile(inr_values, 50),
                            "p99.5 (dB)": np.percentile(inr_values, 99.5),
                            "p99.9 (dB)": np.percentile(inr_values, 99.9)
                        })

    percentile_table = pd.DataFrame(percentile_data)
    percentile_table.to_csv(OUTPUT_ROOT_FOLDER / f"{html_file_prefix}_inr_percentiles.csv", index=False)
    post_processor.add_results_linestyle_getter(linestyle_getter)

    # If set to True the plots will be opened in the browser automatically
    auto_open = False

    # Now plot the results
    post_processor.add_results(results)

    if args.plot_type == "cdf":
        plots = post_processor.generate_cdf_plots_from_results(
            results,
        )
    elif args.plot_type == "ccdf":
        plots = post_processor.generate_ccdf_plots_from_results(
            results,
            n_bins=500,
            cutoff_percentage=0.0005
        )

    post_processor.add_plots(plots)

    # Ensure the "htmls" directory exists relative to the script directory
    htmls_dir = OUTPUT_ROOT_FOLDER / "htmls"
    htmls_dir.mkdir(exist_ok=True)

    # combine imt_ul_sinr and imt_ul_sinr_ext into a single plot with two lines, one for each attribute
    plot_imt_ul_sinr = post_processor.get_plot_by_results_attribute_name("imt_ul_sinr", plot_type=args.plot_type)
    plot_imt_ul_sinr_ext = post_processor.get_plot_by_results_attribute_name("imt_ul_sinr_ext", plot_type=args.plot_type)
    if plot_imt_ul_sinr is not None and plot_imt_ul_sinr_ext is not None:
        sinr_color = []
        if plot_imt_ul_sinr.data:
            for trace in plot_imt_ul_sinr.data:
                if hasattr(trace, 'line') and hasattr(trace.line, 'color'):
                    sinr_color.append(getattr(trace.line, 'color', None))

        for i, trace in enumerate(plot_imt_ul_sinr_ext.data):
            trace.name = f"{trace.name} SINR with external interference"
            trace.line.color = sinr_color[i % len(sinr_color)]
            trace.line.dash = 'dash'
            plot_imt_ul_sinr.add_trace(trace)

        plot_imt_ul_sinr.update_layout(
            title="IMT UL SINR - Inter-cell interference vs Intra-cell + external interference",
            legend_title="",
        )
        plot_imt_ul_sinr.update_xaxes(
            # title="INR[dB]",
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
        plot_imt_ul_sinr.update_yaxes(
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            gridcolor="#DCDCDC",
            gridwidth=1.5
        )
        plot_imt_ul_sinr.update_layout(
            xaxis_title_font=dict(size=24),
            yaxis_title_font=dict(size=24),
            template="plotly_white"
        )
        x_values = []
        for trace in plot_imt_ul_sinr.data:
            if hasattr(trace, 'x') and trace.x is not None:
                try:
                    x_iter = list(trace.x)
                except TypeError:
                    x_iter = [trace.x]
                x_values.extend([float(x) for x in x_iter if x is not None])
        if x_values:
            print(f"Combined plot 'imt_ul_sinr' x-axis data range: {min(x_values)} to {max(x_values)}")
        else:
            print("Combined plot 'imt_ul_sinr' has no x-axis data")
        plot_imt_ul_sinr.write_html(htmls_dir / f"{html_file_prefix}_imt_ul_sinr_combined.html", include_plotlyjs=True)
        # plot_imt_ul_sinr.show()

    # now combine imt_ul_tput and imt_ul_tput_ext into a single plot with two lines, one for each attribute
    plot_imt_ul_tput = post_processor.get_plot_by_results_attribute_name("imt_ul_tput", plot_type=args.plot_type)
    plot_imt_ul_tput_ext = post_processor.get_plot_by_results_attribute_name("imt_ul_tput_ext", plot_type=args.plot_type)
    if plot_imt_ul_tput is not None and plot_imt_ul_tput_ext is not None:
        tput_color = []
        if plot_imt_ul_tput.data:
            for trace in plot_imt_ul_tput.data:
                if hasattr(trace, 'line') and hasattr(trace.line, 'color'):
                    tput_color.append(getattr(trace.line, 'color', None))
        for i, trace in enumerate(plot_imt_ul_tput_ext.data):
            trace.name = f"{trace.name} Throughput with external interference"
            trace.line.color = tput_color[i % len(tput_color)]
            trace.line.dash = 'dash'
            plot_imt_ul_tput.add_trace(trace)
        plot_imt_ul_tput.update_layout(
            title="IMT UL Throughput - Inter-cell interference vs Intra-cell + external interference",
            legend_title="",
        )
        plot_imt_ul_tput.update_xaxes(
            # title="INR[dB]",
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            showticklabels=True,
            tickmode='auto',
            gridcolor="#DCDCDC",
            gridwidth=1.5,
            title_font=dict(size=16),
            tickfont=dict(size=16),
        )
        plot_imt_ul_tput.update_yaxes(
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            gridcolor="#DCDCDC",
            gridwidth=1.5
        )
        plot_imt_ul_tput.update_layout(
            xaxis_title_font=dict(size=24),
            yaxis_title_font=dict(size=24),
            template="plotly_white"
        )
        plot_imt_ul_tput.write_html(htmls_dir / f"{html_file_prefix}_imt_ul_tput_combined.html", include_plotlyjs=True)
        # plot_imt_ul_tput.show()

    # combine imt_ul_intra_interf_power and imt_ul_interf_power into a single plot with two lines, one for each attribute
    imt_ul_intra_interf_power = post_processor.get_plot_by_results_attribute_name("imt_ul_intra_interf_power", plot_type=args.plot_type)
    imt_ul_interf_power = post_processor.get_plot_by_results_attribute_name("imt_ul_interf_power", plot_type=args.plot_type)
    imt_ul_total_interf_power = post_processor.get_plot_by_results_attribute_name("imt_ul_total_interf_power", plot_type=args.plot_type)
    if imt_ul_intra_interf_power is not None and (imt_ul_interf_power is not None or imt_ul_total_interf_power is not None):
        interf_color = []
        if imt_ul_intra_interf_power.data:
            for trace in imt_ul_intra_interf_power.data:
                if hasattr(trace, 'line') and hasattr(trace.line, 'color'):
                    interf_color.append(getattr(trace.line, 'color', None))

        if imt_ul_interf_power is not None:
            for i, trace in enumerate(imt_ul_interf_power.data):
                trace.name = f"{trace.name} Interference Power with external interference"
                trace.line.color = interf_color[i % len(interf_color)] if interf_color else getattr(trace.line, 'color', None)
                trace.line.dash = 'dash'
                imt_ul_intra_interf_power.add_trace(trace)

        if imt_ul_total_interf_power is not None:
            for i, trace in enumerate(imt_ul_total_interf_power.data):
                trace.name = f"{trace.name} Total interference power"
                trace.line.color = interf_color[i % len(interf_color)] if interf_color else getattr(trace.line, 'color', None)
                trace.line.dash = 'dot'
                imt_ul_intra_interf_power.add_trace(trace)

        title = "IMT UL Interference Power - Inter-cell interference vs Intra-cell + external interference"
        if imt_ul_total_interf_power is not None:
            title = "IMT UL Interference Power - Inter-cell, Intra-cell + external, and Total interference power"

        imt_ul_intra_interf_power.update_layout(
            title=title,
            legend_title="",
        )
        imt_ul_intra_interf_power.update_xaxes(
            # title="INR[dB]",
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
        imt_ul_intra_interf_power.update_yaxes(
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            gridcolor="#DCDCDC",
            gridwidth=1.5
        )
        imt_ul_intra_interf_power.update_layout(
            xaxis_title_font=dict(size=24),
            yaxis_title_font=dict(size=24),
            template="plotly_white"
        )
        x_values = []
        for trace in imt_ul_intra_interf_power.data:
            if hasattr(trace, 'x') and trace.x is not None:
                try:
                    x_iter = list(trace.x)
                except TypeError:
                    x_iter = [trace.x]
                x_values.extend([float(x) for x in x_iter if x is not None])
        if x_values:
            print(f"Combined plot 'imt_ul_interf_power' x-axis data range: {min(x_values)} to {max(x_values)}")
        else:
            print("Combined plot 'imt_ul_interf_power' has no x-axis data")
        imt_ul_intra_interf_power.write_html(htmls_dir / f"{html_file_prefix}_imt_ul_interf_power_combined.html", include_plotlyjs=True)
        # imt_ul_intra_interf_power.show()

    for attr in attributes_to_plot:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
        if plot is None:
            print(f"Warning: No plot found for attribute '{attr}'")
            continue
        # Add plot outline and increase font size
        plot.update_xaxes(
            # title="INR[dB]",
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
        # plot.update_layout(
        #     legend=dict(
        #         orientation="h",
        #         x=.2,
        #         y=-1.5,
        #         xanchor="left",
        #         yanchor="bottom",
        #         bgcolor="rgba(255,255,255,0.7)",
        #         bordercolor="black",
        #         borderwidth=1,
        #         font=dict(size=14)
        #     )
        # )
        # plot.update_layout(
        #     width=900,
        #     height=1280
        # )

        x_values = []
        for trace in plot.data:
            if hasattr(trace, 'x') and trace.x is not None:
                try:
                    x_iter = list(trace.x)
                except TypeError:
                    x_iter = [trace.x]
                x_values.extend([float(x) for x in x_iter if x is not None])
        if x_values:
            print(f"Plot '{attr}' x-axis data range: {min(x_values)} to {max(x_values)}")
        else:
            print(f"Plot '{attr}' has no x-axis data")

        if "_inr" in attr and args.plot_type == "ccdf":
            plot.add_hline(
                y=0.001, line_dash="dot", line_color="gray",
                annotation_text="0.1%", annotation_position="left",
            )
            plot.add_vline(
                x=-6, line_dash="dot", line_color="gray",
                annotation_text="-6dB", annotation_position="top right"
            )
        # Make grid lines darker
        plot.write_html(htmls_dir / f"{html_file_prefix}_{attr}.html", include_plotlyjs=True)
        # plot.show()
