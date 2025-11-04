from pathlib import Path
import numpy as np
from sharc.parameters.parameters import Parameters
from campaigns.new_mss_d2d.constants import INPUTS_DIR, get_readable_from_str
import matplotlib.pyplot as plt


pars = [x for x in INPUTS_DIR.iterdir() if "parameter_" in str(x) and "downlink" in str(x)]

mx = 20
mn = 2500
for i, par in enumerate(pars):
    parameters = Parameters()
    param_file = par
    parameters.set_file_name(param_file)
    parameters.read_params()
    params = parameters.mss_d2d

    params.propagate_parameters()
    params.validate("opa")

    N = int(1e3)
    # ns = []
    pmf = np.zeros(8000)
    rng = np.random.RandomState(22)
    grid = params.beam_positioning.service_grid

    for _ in range(N):
        grid.reset_grid("", rng, True)
        n_beams = grid.lon_lat_grid.shape[1]
        n = np.sum(rng.rand(
            n_beams,
        ) < params.beams_load_factor)
        # ns.append(n)
        pmf[n] += 1
        mx = max(mx, n)
        mn = min(mn, n)

    bins = np.arange(0, mx+1)

    fig, ax = plt.subplots(figsize=(8, 3))
    pmf = pmf[:mx+1]
    # print(pmf.shape)
    # print(bins.shape)
    ax.bar(bins, pmf, width=1, edgecolor="black", linewidth=0.25)
    ax.set_xlim(-0.5 + mn, len(pmf) - 0.5)
    ax.set_ylim(0, max(0.01, pmf.max() * 1.05))  # auto-scale a bit
    ax.set_xlabel("Number of beams")
    readable = get_readable_from_str(par.name)
    readable = readable.replace("parameter_new_mss_d2d_", "")
    ax.set_title(readable)
    ax.set_ylabel("Probability")
    fig.tight_layout()
    Path("beams-hist").mkdir(exist_ok=True)

    print(f"saving {i}")
    fig.savefig(f"beams-hist/{i}.png")
    plt.close("all")
