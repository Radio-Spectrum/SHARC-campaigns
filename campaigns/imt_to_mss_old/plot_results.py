import numpy as np
from pathlib import Path

from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

from campaigns.imt_to_mss_cluster_azm_study.constants import (
    CAMPAIGN_DIR,
    SYS_ID_TO_READABLE,
    IMT_ID_TO_READABLE,
    get_specific_pattern
)

# ========================
# Configurações gerais
# ========================
auto_open = True
post_processor = PostProcessor()

# ========================
# Samples para CCDF
# ========================
samples_for_ccdf = [
    "system_dl_interf_power_per_mhz",
    "system_inr",
]

# ========================
# Samples para CDF
# ========================
samples_for_cdf = [
    "imt_system_antenna_gain",
    "imt_system_path_loss",
    "system_dl_interf_power",
    "system_imt_antenna_gain",
    "system_inr",
    "ccdf"
]

# ========================
# Carregar resultados
# ========================
ccdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output/simulation",
    only_latest=True,
    only_samples=samples_for_ccdf
)

cdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output/simulation",
    only_latest=True,
    only_samples=samples_for_cdf
)

# ========================
# Ajuste temporário: converter dBm → dB
# ========================
for res in ccdf_results:
    res.system_dl_interf_power_per_mhz = SampleList(
        np.array(res.system_dl_interf_power_per_mhz) - 30
    )

# ========================
# Estilo de linha dinâmico
# ========================


def linestyle_getter(results):
    styles = ["solid", "dot", "dash", "dashdot"]
    i = 0
    outdir = getattr(results, "output_directory", "")
    if "spurious" in outdir:
        i += 1
    if "microcell" in outdir:
        i += 2
    return styles[i % len(styles)]


post_processor.add_results_linestyle_getter(linestyle_getter)

# ========================
# Função de nome legível (AGORA SIMPLIFICADA)
# ========================


def ensure_readable_name(results):
    name = (
        getattr(results, "readable_name", None)
        or getattr(results, "name", None)
        or getattr(results, "dir_name", None)
        or getattr(results, "output_directory", None)
        or getattr(results, "id", None)
        or "Unnamed"
    )

    # extrai só a última parte (nome da pasta), compatível Windows/Linux
    name = str(name).replace("\\", "/").split("/")[-1].split("mss")[-1]
    name = (f"mss" + name).split("_2025")[0]

    results.readable_name = name

    # >>> ADIÇÃO CRUCIAL: também sobrescreve output_directory para garantir que
    # o PostProcessor use o nome curto (evita mostrar o path completo).
    try:
        results.output_directory = name
    except Exception:
        # se o atributo for read-only, ignore (mas geralmente é mutável)
        pass


# aplica a todos
for r in ccdf_results + cdf_results:
    ensure_readable_name(r)

# ========================
# Legendas com padrões (apenas quando o pattern bater)
# ========================
for topology in ["macrocell", "microcell"]:
    for imt_id in [
        "imt.7300MHz.macrocell",
        "imt.7300MHz.microcell"
    ]:
        if topology not in imt_id:
            continue

        readable_imt = IMT_ID_TO_READABLE.get(imt_id, imt_id)

        for mss_id in [
            "mss.7300MHz.hubType-18",
        ]:
            readable_mss = SYS_ID_TO_READABLE.get(mss_id, mss_id)

            for load in [0.2, 0.5, 1]:
                readable_load = f"Load = {load * 100}%"

                for mask in ["imt", "3gpp", "spurious"]:
                    readable_mask = {
                        "imt": "@IMT Mask",
                        "3gpp": "@3GPP Mask",
                        "spurious": "@Spurious",
                    }[mask]

                    pattern = get_specific_pattern(
                        topology=topology,
                        mss_id=mss_id,
                        imt_id=imt_id,
                        mask=mask,
                        imt_load_factor=load
                    )

                    legend = f"{readable_mss}; {readable_imt}, {readable_load}, {readable_mask}"

                    post_processor.add_plot_legend_pattern(
                        dir_name_contains=pattern,
                        legend=legend
                    )

# ========================
# Gerar gráficos CCDF e CDF
# ========================
ccdf_plots = post_processor.generate_ccdf_plots_from_results(ccdf_results)
cdf_plots = post_processor.generate_cdf_plots_from_results(cdf_results)

post_processor.add_plots(ccdf_plots)
post_processor.add_plots(cdf_plots)

# ========================
# Linha de proteção
# ========================
protection_criteria = -154.0  # dB[W/MHz]
perc_time = 0.01

system_dl_interf_power_per_mhz_plot = post_processor.get_plot_by_results_attribute_name(
    "system_dl_interf_power_per_mhz", plot_type="ccdf"
)

system_dl_interf_power_per_mhz_plot.add_vline(
    protection_criteria,
    line_dash="dash",
    annotation=dict(
        text=f"Protection Criteria: {protection_criteria} dB[W/MHz]",
        xref="x",
        yref="y",
        x=protection_criteria + 0.5,
        y=0.8,
        font=dict(size=12, color="red")
    )
)

system_dl_interf_power_per_mhz_plot.add_hline(
    perc_time,
    line_dash="dash",
    annotation=dict(
        text=f"Time Percentage: {perc_time * 100}%",
        xref="x",
        yref="y",
        x=protection_criteria + 0.5,
        y=perc_time + 0.01,
        font=dict(size=12, color="blue")
    )
)

system_dl_interf_power_per_mhz_plot.update_xaxes(title_text="dB[W/MHz]")

# ========================
# Exportar plots
# ========================
attributes_to_plot = [
    ("imt_system_antenna_gain", "cdf"),
    ("imt_system_path_loss", "cdf"),
    ("system_dl_interf_power", "cdf"),
    ("system_dl_interf_power_per_mhz", "ccdf"),
    ("system_imt_antenna_gain", "cdf"),
    ("system_inr", "cdf"),
    ("system_inr", "ccdf"),
]

HTMLS_DIR = CAMPAIGN_DIR / "output" / "htmls"
HTMLS_DIR.mkdir(parents=True, exist_ok=True)
print(f"Saving plots in {HTMLS_DIR}")

for attr, plot_type in attributes_to_plot:
    file = HTMLS_DIR / f"{attr}.html"
    plot = post_processor.get_plot_by_results_attribute_name(
        attr, plot_type=plot_type)

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
        template="plotly_white",
        legend=dict(
            font=dict(size=14),
            x=0.2,
            y=-0.5,
            orientation='h',
            xanchor='left',
            yanchor='bottom',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='black',
            borderwidth=1
        )
    )

    plot.write_html(file=file, include_plotlyjs="cdn", auto_open=auto_open)
