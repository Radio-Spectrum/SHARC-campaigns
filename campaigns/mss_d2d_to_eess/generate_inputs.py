from campaigns.utils.parameters_factory import ParametersFactory
from campaigns.utils.dump_parameters import dump_parameters
from campaigns.utils.constants import ROOT_DIR

SEED = 0xeffec7  # Example seed value, can be changed as needed
general = {
    "seed": SEED,
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
    "output_dir": "campaigns/mss_d2d_to_eess/output/",
    "output_dir_prefix": "output_mss_d2d_eess",
    "system": "SINGLE_EARTH_STATION",
    "imt_link": "DOWNLINK",
}

factory = ParametersFactory()

params = factory.load_from_id(
    "id: imt.2110-2200MHz.mss-dc.system3"
).load_from_id(
    "eess.system-b"
).load_from_dict(
    {"general": general}
).build()

params["mss_d2d"]["frequency"] = 2167.5
params["mss_d2d"]["bandwidth"] = 5.0
params["mss_d2d"]["cell_radius"] = 39475.0

file = ROOT_DIR / "test_ul.yaml"
dump_parameters(
    file, params
)

file = ROOT_DIR / "test_dl.yaml"
params["general"]["imt_link"] = "DOWNLINK"
dump_parameters(
    file, params
)
