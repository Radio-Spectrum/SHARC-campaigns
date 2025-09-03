"""Script to process and plot results for MSS D2D to IMT cross-border campaign."""

import re
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from sharc.results import Results
from sharc.post_processor import PostProcessor
from campaigns.mss_d2d_to_imt_cross_border.cmd_parser import get_cmd_parser

from campaigns.mss_d2d_to_imt_cross_border.run import CAMPAIGN_STR, get_output_dir_start
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

OUTPUT_ROOT_FOLDER = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR

if __name__ == "__main__":
    post_processor = PostProcessor()

    parser = get_cmd_parser()
    parser.add_argument(
        "--plot_type",
        type=str,
        choices=["cdf", "ccdf"],
        default="cdf",
        help="Type of plot to generate. Choose 'cdf' or 'ccdf'. Default: 'cdf'"
    )
    args = parser.parse_args()

    if len(args.mss) > 1:
        raise ValueError("fiz funfar para um sistema so por enquanto")

    mss_id = args.mss[0]

    def legend_gen(dirname):
        print(dirname)
        pattern = re.compile(
            r"output_mss_d2d_to_imt_cross_border_(\d+\.\d+)km_(\d+\.\d+)load_([ud]l)_"
        )
        match = pattern.match(dirname)
        if not match:
            return "Unknown"

        border_km, load_pct, link_type = match.groups()

        link_type = link_type.upper()
        load_pct = float(load_pct) * 100

        return f"{load_pct}% lf, {border_km} km excl. zone, IMT-{link_type}"

    post_processor.add_plot_legend_generator(legend_gen)

    styles = ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]

    def linestyle_getter(result: Results):
        """
        Returns a line style string based on the prefix found in the result's output directory.
        """
        dirname = result.output_directory
        pattern = re.compile(
            r".*/output_mss_d2d_to_imt_cross_border_(\d+\.\d+)km_(\d+\.\d+)load_([ud]l)_"
        )
        match = pattern.match(dirname)
        if not match:
            return "solid"

        border_km, load_pct, link_type = match.groups()

        if load_pct == "0.2":
            return "dot"
        return "solid"

    post_processor.add_results_linestyle_getter(linestyle_getter)

    campaign_base_dir = str((Path(__file__) / ".." / "..").resolve())

    attributes_to_plot = [
        "imt_system_antenna_gain",
        "system_imt_antenna_gain",
        "sys_to_imt_coupling_loss",
        "imt_system_path_loss",
        "imt_dl_pfd_external",
        "imt_dl_pfd_external_aggregated",
        "imt_dl_inr",
        "imt_ul_inr"
    ]

    output_start = get_output_dir_start(mss_id, not args.adj)

    results_dl = Results.load_many_from_dir(
        OUTPUT_ROOT_FOLDER / f"{output_start}_dl",
        only_latest=True,
        only_samples=attributes_to_plot
    )

    results_ul = Results.load_many_from_dir(
        OUTPUT_ROOT_FOLDER / f"{output_start}_ul",
        only_latest=True,
        only_samples=attributes_to_plot
    )
    # print("len(results_ul)", len(results_ul))
    # ^: typing.List[Results]
    all_results = [*results_ul, *results_dl]

    # Print the percentiles for UL INR
    inr_protection_criteria = -6
    print(f"INR Protection Criteria: {inr_protection_criteria} dB")
    percentiles = [99.5, 99.9, 99.99, 100]
    for res in all_results:
        pattern = re.compile(
            r".*/output_mss_d2d_to_imt_cross_border_(\d+\.\d+)km_(\d+\.\d+)load_([ud]l)_"
        )
        match = pattern.match(res.output_directory)
        if match:
            border_km, load_pct, link_type = match.groups()
        else:
            print(f"Could not parse dirname: {res.output_directory}")
            continue

        if hasattr(res, "imt_ul_inr") and link_type == "ul":
            inr_values = res.imt_ul_inr
            if len(inr_values) == 0:
                print(f"No UL INR values for border={border_km}km, load={load_pct}%, link_type={link_type}")
                continue
            # percentile_values = {p: round(np.percentile(inr_values, p), 2) for p in percentiles}
            percentile_values = np.percentile(inr_values, percentiles)
            print(f"UL INR Percentiles for border={border_km}km, load={float(load_pct) * 100}, link_type={link_type}: {percentile_values}")
            print(f"UL INR Exceedence values for Margin={border_km}km, Load={float(load_pct) * 100}, Link Type={link_type.upper()}")
            print("Percentile, Exceedance (dB)")
            for i, p in enumerate(percentiles):
                print(f"p{p}, {np.round(percentile_values[i] - inr_protection_criteria, 2)}")
        elif hasattr(res, "imt_dl_inr") and link_type == "dl":
            inr_values = res.imt_dl_inr
            if len(inr_values) == 0:
                print(f"No DL INR values for border={border_km}km, load={load_pct}, link_type={link_type}")
                continue
            # percentile_values = {p: round(np.percentile(inr_values, p), 2) for p in percentiles}
            percentile_values = np.percentile(inr_values, percentiles)
            print(f"DL INR Percentiles for Margin={border_km}km, Load={float(load_pct) * 100}%, Link Type={link_type}: {percentile_values}")
            print(f"DL INR Exceedence values for Margin={border_km}km, Load={float(load_pct) * 100}, Link Type={link_type.upper()}")
            print("Percentile, Exceedance (dB)")
            for i, p in enumerate(percentiles):
                print(f"p{p}, {np.round(percentile_values[i] - inr_protection_criteria, 2)}")

    # If set to True the plots will be opened in the browser automatically
    auto_open = False

    post_processor.add_results(all_results)

    if args.plot_type == "cdf":
        plots = post_processor.generate_cdf_plots_from_results(
            all_results,
        )
    elif args.plot_type == "ccdf":
        plots = post_processor.generate_ccdf_plots_from_results(
            all_results,
        )
    else:
        raise ValueError(f"Unknown plot type: {args.plot_type}. Choose 'cdf' or 'ccdf'.")

    post_processor.add_plots(plots)

    # Add a protection criteria line:
    # protection_criteria = -6

    # for attr in ["imt_dl_inr", "imt_ul_inr"]:
    #     plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
    #     if plot is not None:
    #         plot.add_vline(
    #             protection_criteria,
    #             line_dash="dash", annotation=dict(
    #                 text="-6dB Protection criteria",
    #                 font=dict(size=20),
    #                 xref="x",
    #                 yref="paper",
    #                 x=protection_criteria + 0.2,  # Offset for visibility
    #                 y=0.85
    #             )
    #         )
    #     else:
    #         print(f"Warning: No plot found for attribute '{attr}'")

    pfd_protection_criteria = -109
    for attr in ["imt_dl_pfd_external", "imt_dl_pfd_external_aggregated"]:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
        if plot is not None:
            plot.add_vline(pfd_protection_criteria, line_dash="dash", annotation=dict(
                text="PFD protection criteria",
                font=dict(size=18),
                xref="x",
                yref="paper",
                x=pfd_protection_criteria + 1.0,  # Offset for visibility
                y=0.95
            ))
        else:
            print(f"Warning: No plot found for attribute '{attr}'")

    # for attr in attributes_to_plot:
    #     post_processor.get_plot_by_results_attribute_name(attr).show()

    # Ensure the "htmls" directory exists relative to the script directory
    htmls_dir = OUTPUT_ROOT_FOLDER / "htmls"
    htmls_dir.mkdir(exist_ok=True)
    selected_str = output_start
    specific_dir = htmls_dir / selected_str
    specific_dir.mkdir(exist_ok=True)

    for attr in attributes_to_plot:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
        # Add plot outline and increase font size
        plot.update_xaxes(
            title="INR[dB]",
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside',
            showline=True,
            gridcolor="#DCDCDC",
            gridwidth=1.5
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
            legend=dict(font=dict(size=20)),
            template="plotly_white"
        )

        # Make grid lines darker
        if plot is None:
            print(f"Warning: No plot found for attribute '{attr}'")
            continue
        plot.write_html(specific_dir / f"{attr}.html")
        # plot.show()


    # # Now let's plot the beam per satellite results.
    # # We do it manually as PostProcessor does not support histograms yet.
    # # it doesn't matter from where get the results for that statistic.
    # results_num_beams_per_satellite = Results.load_many_from_dir(
    #     os.path.join(campaign_base_dir, f"{output_start}_ul"),
    #     only_latest=True,
    #     only_samples=["mss_d2d_num_beams_per_satellite"],
    #     filter_fn=(lambda dir_name: "output_mss_d2d_to_imt_cross_border_0km_service_grid_padded_50p" in dir_name)
    # )

    # mss_d2d_num_beams_per_satellite_attr = getattr(results_num_beams_per_satellite[0],
    #                                                "mss_d2d_num_beams_per_satellite", None)

    # if results_num_beams_per_satellite is not None:
    #     fig = go.Figure()
    #     fig.add_trace(go.Histogram(
    #         x=mss_d2d_num_beams_per_satellite_attr,
    #         nbinsx=15,
    #         histnorm='probability',
    #         marker_color='blue',
    #         opacity=0.75
    #     ))
    #     fig.update_layout(
    #         title="Number of Beams per Satellite Histogram",
    #         xaxis_title="Number of Beams per Satellite",
    #         yaxis_title="Frequency",
    #         # template="plotly_white",
    #         bargap=0.2,
    #     )
    #     fig.write_html(specific_dir / "mss_d2d_num_beams_per_satellite_hist.html")
    #     if auto_open:
    #         fig.show()
