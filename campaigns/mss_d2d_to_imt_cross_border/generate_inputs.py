from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.utils.constants import ROOT_DIR


general = {
    "seed": 101,
    ###########################################################################
    # Number of simulation snapshots
    ###########################################################################
    "num_snapshots": 10000,
    "enable_cochannel": True,
    "enable_adjacent_channel": False,
    ###########################################################################,
    # if FALSE, then a new output directory is created,
    "overwrite_output": False,
    ###########################################################################,
    # output destination folder - this is relative SHARC/sharc directory,
    "output_dir": "campaigns/mss_d2d_to_imt_cross_border/output_base_ul/",
    "output_dir_prefix": "output_mss_d2d_to_imt_cross_border_base_ul",
    "system": "MSS_D2D",
    "imt_link": "UPLINK",
}

factory = ParametersFactory()

params = factory.load_from_id(
        "imt.1-3GHz.single-bs.aas-macro-bs"
    ).load_from_id(
        "mss-dc.system-a"
    ).load_from_dict(
        {"general": general}
    ).build()

params["mss_d2d"]["frequency"] = 2167.5
params["mss_d2d"]["bandwidth"] = 5.0
params["mss_d2d"]["cell_radius"] = 39475.0

params["imt"]["frequency"] = 2160.0
params["imt"]["bandwidth"] = 20.0

file = ROOT_DIR / "test_ul.yaml"
dump_parameters(
    file, params
)

file = ROOT_DIR / "test_dl.yaml"
params["general"]["imt_link"] = "DOWNLINK"
dump_parameters(
    file, params
)
