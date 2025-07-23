import yaml

def dump_parameters(filepath, data: dict):
    with open(filepath, "w") as f:
        yaml.dump(data, f, sort_keys=False)
