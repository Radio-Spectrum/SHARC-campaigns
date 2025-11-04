"""
This Factory is supposed to be used to create your own parameters
file
"""

from pathlib import Path
import yaml
import re

from sharc.parameters.parameters import Parameters
from campaigns.utils.constants import ROOT_PARAMS_DIR, ROOT_DIR
from campaigns.utils.tracking_proxy import TrackingProxy


class ParametersFactory():
    _base_dir: Path
    _VALID_ID_REGEX = re.compile(r'^[a-zA-Z0-9-.]+$')
    _ids_to_dir = {}
    _data = {}

    def __init__(
        self,
        base_dir=ROOT_PARAMS_DIR
    ):
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)

        self.set_base_dir(
            base_dir
        )
        self._reset()

    def _reset(self):
        self._data = {
            "metadata": {
                "based_on_ids": [],
            },
        }

    def _get_param_dir(self, id: str) -> str | None:
        return self._ids_to_dir[id]

    def _validate_param_dict(
        self, param: dict
    ) -> None:
        ks = param.keys()

        # NOTE: from previous parsing, id is already expected to exist
        # this code still kinda looks bad.
        # TODO: returning errors as values would do better here
        # TODO: enforce metadata expected information
        for expected in ["id", "metadata"]:
            if expected not in ks:
                raise ValueError(
                    f"Didn't find required keys in parameter '{param['id']}'"
                )
        if len(ks) != 3:
            raise ValueError(
                f"Wrong number of keys in parameter '{param['id']}'"
            )
        # TODO: validate if system name is correct by
        # checking parameters section_name

    def _write_to_file(
        self, fname
    ):
        with open(fname, "w") as f:
            yaml.dump(self._data, f, sort_keys=False)

    def _get_param_as_dict(
        self, dir: str
    ) -> dict:
        with open(dir, "r") as f:
            data = yaml.safe_load(f)

        self._validate_param_dict(data)

        return data

    def set_base_dir(
        self,
        base_dir: Path,
    ) -> "ParametersFactory":
        self.base_dir = base_dir
        self._ids_to_dir = {}

        for file_path in base_dir.rglob("*.yaml"):
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if line == "" or line.startswith("#"):
                        # ignore comments or empty lines at the start
                        continue
                    # if it is not comment, first line must be its id
                    if line.startswith("id:"):
                        _, value = line.split(":", 1)
                        id = value.strip()
                        if not self._VALID_ID_REGEX.fullmatch(id):
                            raise ValueError(
                                f"Error when parsing {file_path}:\n"
                                f"\tInvalid id '{id}'!"
                            )
                        if id in self._ids_to_dir:
                            raise ValueError(
                                f"Error when parsing {file_path}:\n"
                                f"\t id '{id}' is also used in '{self._ids_to_dir[id]}'\n"
                            )
                        self._ids_to_dir[id] = file_path
                        break
                    else:
                        raise ValueError(
                            f"Error when parsing {file_path}:\n"
                            "\tThe first line of each yaml file MUST be its id."
                        )

    def load_from_id(
        self, id: str
    ) -> "ParametersFactory":
        dir = self._get_param_dir(id)
        if dir is None:
            raise ValueError(
                f"No file found with id '{id}'"
            )

        self.load_from_dir(dir, validate=True)

        return self

    def load_from_dir(
        self, dir: str | Path, validate=False
    ) -> "ParametersFactory":
        params = self._get_param_as_dict(dir)
        self.load_from_dict(params, validate=validate)

        return self

    def load_from_dict(
        self, data: dict, validate=False
    ) -> "ParametersFactory":
        if validate:
            self._validate_param_dict(data)
        id = data.pop("id", None)
        metadata = data.pop("metadata", None)
        sys_key, sys_data = next(iter(data.items()))

        if sys_key in self._data:
            # TODO: permit overwrite with another method
            raise ValueError(
                f"Loading parameter {id} would overwrite existing {sys_key} data"
            )
        self._data[sys_key] = sys_data

        if None not in [id, metadata]:
            self._data["metadata"][id] = metadata

        if id is not None:
            self._data["metadata"]["based_on_ids"].append(
                id
            )

        return self

    # TODO: would much rather work with Parameters instance than
    # dict after building, but then would need a dump parameters
    # functionality in Parameters class, or a proxy observer
    # NOTE: a proxy/observer could update Parameters and
    # dict at the same time..?
    def build(
        self, filepath=".tmp.yaml"
    ) -> Parameters:
        """
        Resets factory data, and returns previous accumulated data
        """
        self._write_to_file(filepath)

        params = Parameters()
        params.set_file_name(filepath)
        params.read_params()

        starting_data = self._data
        self._reset()

        return TrackingProxy(
            params, starting_data
        )
