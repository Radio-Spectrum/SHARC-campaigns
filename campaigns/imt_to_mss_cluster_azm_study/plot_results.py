import numpy as np
from pathlib import Path

from sharc.results import Results, SampleList
from sharc.post_processor import PostProcessor

# Certifique-se de que 'plotly.graph_objects' (go) ou 'plotly.express' (px)
# pode ser acessado pelo seu objeto 'plot' customizado.
# Assumimos que 'plot' possui um método 'add_trace' ou 'figure' interno para isso.
import plotly.graph_objects as go

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
# Samples para CCDF e CDF (Inalterados)
# ========================
samples_for_ccdf = [
    "system_dl_interf_power_per_mhz",
    "system_inr",
]
samples_for_cdf = [
    "imt_system_antenna_gain",
    "imt_system_path_loss",
    "system_dl_interf_power",
    "system_imt_antenna_gain",
    "system_inr",
    "ccdf"
]

# ========================
# Carregar resultados (Inalterado)
# ========================
ccdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output/both_ends",
    only_latest=True,
    only_samples=samples_for_ccdf
)

cdf_results = Results.load_many_from_dir(
    CAMPAIGN_DIR / "output/both_ends",
    only_latest=True,
    only_samples=samples_for_cdf
)

# ========================
# Ajuste temporário: converter dBm → dB (Inalterado)
# ========================
for res in ccdf_results:
    res.system_dl_interf_power_per_mhz = SampleList(
        np.array(res.system_dl_interf_power_per_mhz) - 30
    )

# ========================
# Estilo de linha dinâmico (Inalterado)
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
# Função de nome legível (Inalterado, mas atenção à lógica condicional)
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
    name = str(name).replace("\\", "/").split("/")[-1].split("mss")[-1]
    name = (f"mss" + name).split("_2025")[0]

    # print(name) # Mantido para debug, mas pode ser removido

    # Aplica o novo nome legível baseado no sufixo numérico
    name_pos = None

    if "_pos0" in name:
        name_pos = "(0° degree)"
    if "_pos90" in name:
        name_pos = "(90° degree)"
    if "_pos180" in name:
        name_pos = "(180° degree)"

    if "3100" in name:
        name = "1.5 km, 50% load"
    elif "3600" in name:
        name = "2 km, 50% load"
    elif "6600" in name:
        name = "5 km, 50% load"

    results.readable_name = name
    # Sobrescreve output_directory para PostProcessor
    try:
        results.output_directory = name
    except Exception:
        pass


for r in ccdf_results + cdf_results:
    ensure_readable_name(r)

# ========================
# Legendas com padrões (Inalterado)
# ========================
for topology in ["macrocell", "microcell"]:
    for imt_id in ["imt.7300MHz.macrocell", "imt.7300MHz.microcell"]:
        if topology not in imt_id:
            continue

        readable_imt = IMT_ID_TO_READABLE.get(imt_id, imt_id)

        for mss_id in ["mss.7300MHz.hubType-18"]:
            readable_mss = SYS_ID_TO_READABLE.get(mss_id, mss_id)

            for load in [0.2, 0.5, 1]:
                readable_load = f"Load = {int(load * 100)}%"

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
# Gerar gráficos CCDF e CDF (Inalterado)
# ========================
ccdf_plots = post_processor.generate_ccdf_plots_from_results(ccdf_results)
cdf_plots = post_processor.generate_cdf_plots_from_results(cdf_results)

post_processor.add_plots(ccdf_plots)
post_processor.add_plots(cdf_plots)

# =================================================================
# FUNÇÕES AUXILIARES PARA LINHAS DE PROTEÇÃO E LEGENDAS
# =================================================================

# Define os critérios e cores
CRITERIA_LINES = {
    # Protection: -154.0 dB[W/MHz] @ 1% time
    "Protection -154": {
        "x_value": -154.0,
        "y_ccdf": 0.01,
        "color": "red",
        "legend": "Protection: -154 dB[W/MHz] @ 1%"
    },
    # Protection: -7 dB @ 0.1% time
    "Protection -7": {
        "x_value": -7.0,
        "y_ccdf": 0.001,
        "color": "blue",
        "legend": "Protection Criteria -7 dB @ 0.1%"
    },
    # Protection: -10.5 dB @ 20% time
    "Protection -10.5": {
        "x_value": -10.5,
        "y_ccdf": 0.20,
        "color": "green",
        "legend": "Protection Criteria -10.5 dB @ 20%"
    },
    # Protection: -10.5 dB @ 20% time
    "Protection -6": {
        "x_value": -6,
        "y_ccdf": 0.0003,
        "color": "green",
        "legend": "Protection Criteria -6 dB @ 0.03%"
    }
}


def add_protection_criteria_line(plot, x_value, y_value, line_color, legend_text, plot_type):
    """Adiciona as linhas V/H como shapes e um trace fantasma para a legenda."""

    # 1. Adicionar o trace fantasma para aparecer na legenda
    # O trace deve ser invisível, mas com cor e tipo de linha corretos.
    # O valor Y (probabilidade) não importa, desde que não interfira no gráfico.

    # Se o objeto plot tiver um método add_trace nativo (como o Figure do Plotly):
    plot.add_trace(
        go.Scatter(
            x=[None],  # Fantasma
            y=[None],  # Fantasma
            mode='lines',
            line=dict(color=line_color, width=2, dash='dash'),
            name=legend_text,
            showlegend=True
        )
    )

    # 2. Adicionar as linhas de shape (marcação visual no gráfico)

    # Linha vertical
    plot.add_vline(
        x=x_value,
        line_color=line_color,
        line_dash="dash",
        line_width=1.5
    )

    # Linha horizontal (Ajusta o valor de Y se for CDF)
    if plot_type == 'cdf':
        y_shape = 1 - y_value
    else:  # ccdf
        y_shape = y_value

    plot.add_hline(
        y=y_shape,
        line_color=line_color,
        line_dash="dash",
        line_width=1.5
    )


def add_protection_lines(plot, attr, plot_type):
    """Aplica os critérios de proteção ao gráfico, usando a nova função auxiliar."""

    # Condição 1: Apenas Linha -154 dB[W/MHz]
    if (attr == "system_dl_interf_power_per_mhz" and plot_type == "ccdf"):
        crit = CRITERIA_LINES["Protection -154"]
        add_protection_criteria_line(
            plot,
            crit["x_value"],
            crit["y_ccdf"],
            crit["color"],
            crit["legend"],
            plot_type
        )

    # Condição 2: Linhas -7 dB e -10.5 dB (para system_dl_interf_power_per_mhz CCDF e system_inr CDF/CCDF)
    if (attr == "system_dl_interf_power_per_mhz" and plot_type == "ccdf") or \
       (attr == "system_inr"):

        # Par 1: -7 dB @ 0.1%
        crit1 = CRITERIA_LINES["Protection -7"]
        add_protection_criteria_line(
            plot,
            crit1["x_value"],
            crit1["y_ccdf"],
            crit1["color"],
            crit1["legend"],
            plot_type
        )

        # Par 2: -10.5 dB @ 20%
        crit2 = CRITERIA_LINES["Protection -10.5"]
        add_protection_criteria_line(
            plot,
            crit2["x_value"],
            crit2["y_ccdf"],
            crit2["color"],
            crit2["legend"],
            plot_type
        )


# ========================
# Exportar plots (HTML + PNG)
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

PNG_DIR = CAMPAIGN_DIR / "output" / "png"
PNG_DIR.mkdir(parents=True, exist_ok=True)

print(f"Saving plots in {HTMLS_DIR} and {PNG_DIR}")

for attr, plot_type in attributes_to_plot:
    file_html = HTMLS_DIR / f"{attr}_{plot_type}.html"
    file_png = PNG_DIR / f"{attr}_{plot_type}.png"

    plot = post_processor.get_plot_by_results_attribute_name(
        attr, plot_type=plot_type)

    if plot is None:
        print(f"Plot not found for {attr}, type {plot_type}. Skipping...")
        continue

    # Adiciona as linhas de proteção
    add_protection_lines(plot, attr, plot_type)

    # Atualiza o título do eixo X
    if attr == "system_dl_interf_power_per_mhz":
        plot.update_xaxes(title_text="Interference Power Density (dB[W/MHz])")
    elif attr == "system_inr":
        plot.update_xaxes(title_text="INR (dB)")

    # Configurações de estilo (Eixo X inalterado)
    plot.update_xaxes(
        linewidth=1, linecolor='black', mirror=True,
        ticks='inside', showline=True, gridcolor="#DCDCDC",
        gridwidth=1.5, title_font=dict(size=16),
        tickfont=dict(size=16),
    )

    # 🎯 ALTERAÇÃO FEITA AQUI: Eixo Y em escala logarítmica (base 10)
    plot.update_yaxes(
        linewidth=1, linecolor='black', mirror=True,
        ticks='inside', showline=True, gridcolor="#DCDCDC",
        gridwidth=1.5,
        type='log'  # <--- Adicionado para escala logarítmica
    )

    plot.update_layout(
        xaxis_title_font=dict(size=24),
        yaxis_title_font=dict(size=24),
        template="plotly_white",
        # Move a legenda para a parte inferior e horizontal para acomodar as novas entradas
        legend=dict(
            font=dict(size=14),
            # Ajustado para x=0 (começa na borda esquerda)
            x=0, y=-0.5, orientation='h',
            xanchor='left', yanchor='bottom',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='black', borderwidth=1
        )
    )

    plot.write_html(file=file_html, include_plotlyjs="cdn",
                    auto_open=auto_open)
    plot.write_image(str(file_png), format="png", scale=3)

print("All plots saved!")
