"""Script to process and plot results for MSS D2D to IMT cross-border campaign."""

import re
from pathlib import Path
import plotly.graph_objects as go
from sharc.results import Results
from sharc.post_processor import PostProcessor
from campaigns.mss_d2d_to_imt_cross_border.cmd_parser import get_cmd_parser  # we reuse the same parser

from campaigns.mss_d2d_to_imt_separation_distance.run import CAMPAIGN_STR, get_output_dir_start
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

OUTPUT_ROOT_FOLDER = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR

# OUTPUT_FOLDER_REGEX_PATTERN = r"output_mss_d2d_to_imt_separation_distance_(\d+\.\d+)km_(ul|dl)_"
# OUTPUT_FOLDER_REGEX_PATTERN = r"output_mss_d2d_to_imt_separation_distance_(\d+)km_(ul|dl)_"
OUTPUT_FOLDER_REGEX_PATTERN = r"output_mss_d2d_to_imt_separation_distance_((?:neg\d+\.)?\d+)km_(urban|suburban|rural)_(ul|dl)_"

SEPARATION_DISTANCES_KM = ['neg0.4'] + list((str(s) for s in [0, 1, 5, 10, 20, 50, 100]))

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
        """
        Generates a legend string based on the separation distance and link type found in the directory name.
        Parameters
        ----------
        dirname : str
            The directory name to extract information from.

        Returns
        -------
        str
            String formatted as "{separation_dist}km separation dist., IMT TN {link_type}"
        """
        print("Generating legend for data in:", dirname)
        pattern = re.compile(
            OUTPUT_FOLDER_REGEX_PATTERN
        )
        match = pattern.match(dirname)
        if not match:
            print("Warning: Directory name does not match expected pattern.")
            return "Unknown"

        sep_dist, link_type, deployment = match.groups()
        link_type = link_type.upper()
        deployment = deployment.upper()

        legend_str = f"{sep_dist}km separation dist., IMT TN {link_type} - {deployment}".replace("neg", "-")

        print("Generated legend:", legend_str)

        return legend_str

    post_processor.add_plot_legend_generator(legend_gen)

    styles = ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]

    def linestyle_getter(result: Results):
        """
        Returns a line style string based on the prefix found in the result's output directory.
        """
        dirname = result.output_directory
        pattern = re.compile(
            r".*" + OUTPUT_FOLDER_REGEX_PATTERN
        )
        match = pattern.match(dirname)
        if not match:
            return "solid"

        _, deployment, _ = match.groups()

        for idx, val in enumerate(["urban", "suburban", "rural"]):
            print(val, deployment)
            if val == deployment:
                return styles[idx % len(styles)]

        return "solid"

    post_processor.add_results_linestyle_getter(linestyle_getter)

    campaign_base_dir = str((Path(__file__) / ".." / "..").resolve())

    attributes_to_plot = [
        # "imt_system_antenna_gain",
        # "system_imt_antenna_gain",
        # "sys_to_imt_coupling_loss",
        # "imt_system_path_loss",
        "imt_dl_pfd_external",
        "imt_dl_pfd_external_aggregated",
        "imt_dl_inr",
        "imt_ul_inr"
    ]

    results = Results.load_many_from_dir(
        OUTPUT_ROOT_FOLDER / "output",
        only_latest=True,
        only_samples=attributes_to_plot
    )

    # print("len(results_ul)", len(results_ul))
    # ^: typing.List[Results]
    all_results = [*results]

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
            # n_bins=200,
            cutoff_percentage=(1 - 0.9995)  # Show up to 99.95% on CCDF
        )
    else:
        raise ValueError(f"Unknown plot type: {args.plot_type}. Choose 'cdf' or 'ccdf'.")

    post_processor.add_plots(plots)

    # Add a protection criteria line:
    protection_criteria = -6

    for attr in ["imt_dl_inr", "imt_ul_inr"]:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
        if plot is not None:
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
        else:
            print(f"Warning: No plot found for attribute '{attr}'")

    pfd_protection_criteria = -109
    for attr in ["imt_dl_pfd_external", "imt_dl_pfd_external_aggregated"]:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
        if plot is not None:
            plot.add_vline(pfd_protection_criteria, line_dash="dash", annotation=dict(
                text=f"{pfd_protection_criteria}dB[W/m2/MHZ] protection criteria",
                font=dict(size=12),
                xref="x",
                yref="paper",
                x=pfd_protection_criteria - 20.0,  # Offset for visibility
                y=0.95
            ))
        else:
            print(f"Warning: No plot found for attribute '{attr}'")

    # for attr in attributes_to_plot:
    #     post_processor.get_plot_by_results_attribute_name(attr).show()

    # Ensure the "htmls" directory exists relative to the script directory
    htmls_dir = OUTPUT_ROOT_FOLDER / "output" / "htmls"
    htmls_dir.mkdir(exist_ok=True)
    specific_dir = htmls_dir
    specific_dir.mkdir(exist_ok=True)

    for attr in attributes_to_plot:
        plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type=args.plot_type)
        # Add plot outline and increase font size
        plot.update_xaxes(
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
        # Set line color for specific legend
        for trace in plot.data:
            if trace.name == "-0.4km separation dist., IMT TN UL":
                trace.line.color = "blue"

        # Make grid lines darker
        if plot is None:
            print(f"Warning: No plot found for attribute '{attr}'")
            continue
        html_file_name = specific_dir / f"{attr}_{args.plot_type}.html"
        print(f"Saving plot for attribute: {attr} in {html_file_name}")
        plot.write_html(html_file_name)
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
