import yaml
from sharc.parameters.parameters import Parameters
from campaigns.utils.tracking_proxy import TrackingProxy

def dump_parameters(filepath, params: Parameters | TrackingProxy):
    """
    Dumps proxied parameters data to a file.

    Parameters included in typing only for ease of understanding.
    This method only accepts proxied Parameters
    """
    if not isinstance(params, TrackingProxy):
        raise ValueError(
            "You must pass a proxied object to the dump_parameters method"
        )
    with open(filepath, "w") as f:
        yaml.dump(params.get_data_dict(), f, sort_keys=False)
