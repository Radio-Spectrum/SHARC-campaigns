"""Script to process and plot results for MSS D2D to IMT cross-border campaign."""

import os
from pathlib import Path
import plotly.graph_objects as go
from sharc.results import Results
from sharc.post_processor import PostProcessor
from campaigns.mss_d2d_to_imt_cross_border.cmd_parser import get_cmd_parser

from campaigns.mss_d2d_to_imt_cross_border.run import CAMPAIGN_STR, get_output_dir_start
from campaigns.utils.constants import SHARC_SIM_ROOT_DIR

OUTPUT_ROOT_FOLDER = SHARC_SIM_ROOT_DIR / CAMPAIGN_STR

post_processor = PostProcessor()

parser = get_cmd_parser()
args = parser.parse_args()

distances_map = {
    "system-3.2110-2200MHz.525km": [36.726, 57.817, 78.909, 100.0],
    "system-3.2110-2200MHz.340km": [48.438, 65.625, 82.813, 100.0],
    "system-4.2110-2200MHz.690km": [23.784, 49.189, 74.595, 100.0],
}
if len(args.mss) > 1:
    raise ValueError("fiz funfar para um sistema so por enquanto")

mss_id = args.mss[0]
distances = distances_map[mss_id]

print("Plotting scenarios of grid border as ", distances)
for load in [0.2, 0.5]:
    for link in ["dl", "ul"]:
        for border in distances:
            out_prefix = f"output_mss_d2d_to_imt_cross_border_{border}km_{load}load_{link}"
            post_processor\
                .add_plot_legend_pattern(
                    dir_name_contains=out_prefix,
                    legend=f"{border}km border; {int(load*100)}% load"
                )

prefixes = [f"{d}km" for d in distances]
styles = ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]

def linestyle_getter(result: Results):
    """
    Returns a line style string based on the prefix found in the result's output directory.
    """
    for i in range(len(prefixes)):
        if "_" + prefixes[i] in result.output_directory:
            return styles[i]
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
# print("len(results_dl)", len(results_dl))
# for i in range(len(results_dl)):
#     print(results_dl[i].imt_dl_inr)
# exit()
results_ul = Results.load_many_from_dir(
    OUTPUT_ROOT_FOLDER / f"{output_start}_ul",
    only_latest=True,
    only_samples=attributes_to_plot
)
# print("len(results_ul)", len(results_ul))
# ^: typing.List[Results]
all_results = [*results_ul, *results_dl]

# If set to True the plots will be opened in the browser automatically
auto_open = False

post_processor.add_results(all_results)

plots = post_processor.generate_ccdf_plots_from_results(
    all_results
)
post_processor.add_plots(plots)

# Add a protection criteria line:
protection_criteria = -6
perc_of_time = 0.01

for attr in ["imt_dl_inr", "imt_ul_inr"]:
    plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type='ccdf')
    if plot is not None:
        plot.add_vline(protection_criteria, line_dash="dash", annotation=dict(
            text="Protection criteria",
            xref="x",
            yref="paper",
            x=protection_criteria + 1.0,  # Offset for visibility
            y=0.95
        ))
        plot.add_hline(perc_of_time, line_dash="dash")
    else:
        print(f"Warning: No plot found for attribute '{attr}'")

pfd_protection_criteria = -109
for attr in ["imt_dl_pfd_external", "imt_dl_pfd_external_aggregated"]:
    plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type='ccdf')
    if plot is not None:
        plot.add_vline(pfd_protection_criteria, line_dash="dash", annotation=dict(
            text="PFD protection criteria",
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
    plot = post_processor.get_plot_by_results_attribute_name(attr, plot_type="ccdf")
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
