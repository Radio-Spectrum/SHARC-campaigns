from itertools import product
import numpy as np
from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

# Assuming this is a plotly Figure object, adding for type hinting
from plotly.graph_objects import Figure

from campaigns.mss_d2d_to_mss.constants import (
    CAMPAIGN_DIR, MSS_ES_TO_READABLE, IMT_MSS_DC_ID_TO_READABLE,
    IMT_MSS_DC_IDS, MSS_DC_LOAD_FACTORS, SINGLE_ES_MSS_IDS,
    get_specific_pattern,
)

folder_name = "--name--"

folder = f"results_adj_channel/{folder_name}"

# Note: For saving static images, ensure you have kaleido installed.
# You can install it with: pip install kaleido

auto_open = False

post_processor = PostProcessor()

# Attributes to plot (CDF + CCDF)
attributes_to_plot = [
    ("imt_system_antenna_gain", "cdf"),
    ("imt_system_path_loss", "cdf"),
    ("system_imt_antenna_gain", "cdf"),
    ("system_inr", "cdf"),
    ("system_inr", "ccdf"),
    ("system_ul_interf_power_per_mhz", "cdf"),
    ("system_pfd", "cdf"),
    ("system_dl_interf_power_per_mhz", "ccdf"),
    ("system_ul_interf_power_per_mhz", "ccdf"),
    ("system_pfd", "ccdf"),
]

# Get a single, unique set of all samples required for all plots.
all_samples_to_load = {attr[0] for attr in attributes_to_plot}

# Load all required results ONCE, instead of multiple times.
results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output" / folder,
    only_latest=True,
    only_samples=list(all_samples_to_load)
)


# Apply unit fixes to ALL loaded results.
for res in results:
    # Convert dBm → dB[W] for DL power
    if hasattr(res, "system_dl_interf_power_per_mhz"):
        res.system_dl_interf_power_per_mhz = SampleList(
            np.array(res.system_dl_interf_power_per_mhz) - 30
        )

    # Convert dBm → dB[W] for UL power
    if hasattr(res, "system_ul_interf_power_per_mhz"):
        res.system_ul_interf_power_per_mhz = SampleList(
            np.array(res.system_ul_interf_power_per_mhz) - 30
        )

    # Convert INR to dB (dimensionless) if simulator exported it like dBm
    if hasattr(res, "system_inr"):
        arr = np.array(res.system_inr)
        # INR should be around -20 .. +20 dB normally
        if arr.max() > 50:  # looks like dBm offset
            res.system_inr = SampleList(arr - 30)


def linestyle_getter(results_obj):
    """Choose line style based on folder name."""
    i = 0
    styles = ["solid", "dot", "dash", "dashdot"]
    if "spurious_mask" in results_obj.output_directory:
        i += 1
    if "340km" in results_obj.output_directory:
        i += 2
    return styles[i]


post_processor.add_results_linestyle_getter(linestyle_getter)

# Legend labels
for mss_dc_id, mss_es_id, load_factor in product(
    IMT_MSS_DC_IDS, SINGLE_ES_MSS_IDS, MSS_DC_LOAD_FACTORS
):
    readable_mss = IMT_MSS_DC_ID_TO_READABLE[mss_dc_id]
    readable_sys = MSS_ES_TO_READABLE[mss_es_id]
    readable_load = f"Load = {load_factor * 100}%"
    post_processor.add_plot_legend_pattern(
        dir_name_contains=get_specific_pattern(
            mss_dc_id, mss_es_id, load_factor),
        legend=f"{readable_sys}; {readable_mss}, {readable_load}"
    )

# Generate plots using the single, fully-corrected list of results
plots_ccdf = post_processor.generate_ccdf_plots_from_results(results)
post_processor.add_plots(plots_ccdf)

plots_cdf = post_processor.generate_cdf_plots_from_results(results)
post_processor.add_plots(plots_cdf)


# Update specific plot axes
system_dl_interf_power_per_mhz = post_processor.get_plot_by_results_attribute_name(
    "system_dl_interf_power_per_mhz", plot_type="ccdf"
)
if system_dl_interf_power_per_mhz is not None:
    system_dl_interf_power_per_mhz.update_xaxes(
        title_text="Interference Power [dB(W/MHz)]",
    )

system_inr_plot = post_processor.get_plot_by_results_attribute_name(
    "system_inr", plot_type="ccdf"
)
if system_inr_plot is not None:
    system_inr_plot.update_xaxes(
        title_text="INR [dB]",
    )
    # Add protection criteria lines
    system_inr_plot.add_vline(
        x=-12.2,
        line_width=2,
        line_dash="dash",
        line_color="black",
        annotation_text="Protection Criteria: -12.2 dB",
        annotation_position="top left",
        annotation_font_size=14,
    )
    system_inr_plot.add_vline(
        x=-6,
        line_width=2,
        line_dash="dash",
        line_color="black",
        annotation_text="Protection Criteria: -6 dB",
        annotation_position="top left",
        annotation_font_size=14,
    )
    system_inr_plot.add_hline(
        y=0.01,
        line_width=1.5,
        line_dash="dot",
        line_color="red",
        annotation_text="1% of time",
        annotation_position="bottom right",
        annotation_font_size=14,
    )


def style_plot(plot: Figure) -> Figure:
    """Applies a consistent style to a Plotly figure."""
    plot.update_xaxes(
        linewidth=1,
        linecolor='black',
        mirror=True,
        ticks='inside',
        showline=True,
        gridcolor="#DCDCDC",
        gridwidth=1.5,
        title_font=dict(size=18),
        tickfont=dict(size=16),
    )
    plot.update_yaxes(
        linewidth=1,
        linecolor='black',
        mirror=True,
        ticks='inside',
        showline=True,
        gridcolor="#DCDCDC",
        gridwidth=1.5,
        tickfont=dict(size=16),
    )
    plot.update_layout(
        xaxis_title_font=dict(size=24),
        yaxis_title_font=dict(size=24),
        template="plotly_white",
        legend=dict(
            font=dict(size=14),
            x=0.5,
            y=-0.4,
            orientation='h',
            xanchor='center',
            yanchor='bottom',
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='black',
            borderwidth=1
        )
    )
    return plot


# --- SAVING PLOTS AND IMAGES ---

# Create a single directory for all results
RESULTS_DIR = CAMPAIGN_DIR / "output" / folder / folder_name
RESULTS_DIR.mkdir(exist_ok=True, parents=True)
print(f"Saving all outputs in: {RESULTS_DIR}")

# Loop, get plot, apply styles, and save all versions.
for attr, plot_type in attributes_to_plot:
    plot = post_processor.get_plot_by_results_attribute_name(
        attr, plot_type=plot_type)
    if plot is None:
        continue

    # 1. Apply the standard light theme style
    styled_plot = style_plot(plot)

    # 2. Define base filename
    base_filename = f"{attr}-{plot_type}"

    # 3. Save the interactive HTML file (light theme by default)
    html_file = RESULTS_DIR / f"{base_filename}.html"
    styled_plot.write_html(
        file=html_file, include_plotlyjs="cdn", auto_open=auto_open)

    # 4. Save the light theme image in 1920x1080
    light_img_file = RESULTS_DIR / f"{base_filename}_light.png"
    styled_plot.write_image(light_img_file, width=1920, height=1080)

    # 5. Switch to dark theme and save the dark theme image in 1920x1080
    styled_plot.update_layout(template="plotly_dark")
    dark_img_file = RESULTS_DIR / f"{base_filename}_dark.png"
    styled_plot.write_image(dark_img_file, width=1920, height=1080)
