from typing import Any
from sharc.parameters.parameters import Parameters

class TrackingProxy:
    def __init__(self, obj: Any, data: dict = None, path: str = ""):
        self._obj = obj
        self._path = path
        self._data = data if data is not None else {}

    def __setattr__(self, name, value):
        if name in {"_obj", "_path", "_data"}:
            # set normally in own class
            super().__setattr__(name, value)
            return

        # let it pass to wrapped obj
        setattr(self._obj, name, value)

        full_path = f"{self._path}.{name}" if self._path else name

        # record change
        self._update_data(full_path, value)

        if hasattr(value, "__dict__"):
            raise ValueError(
                "Setting a property value that contains nested values is not supported!"
            )

    def __getattr__(self, name):
        attr = getattr(self._obj, name)
        if self._is_trackable(attr):
            proxy = TrackingProxy(
                attr,
                data=self._data,
                path=f"{self._path}.{name}" if self._path else name,
            )
            object.__setattr__(self, name, proxy)
            return proxy
        return attr

    def get_data_dict(self):
        return self._data

    def _update_data(self, path, value):
        parts = path.split(".")
        d = self._data
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value

    def _is_trackable(self, value):
        return (
            hasattr(value, "__dict__")
            and not callable(value)
            and not isinstance(value, TrackingProxy)
        )

if __name__ == "__main__":
    prm: Parameters = TrackingProxy(Parameters(), {"opa": "teste"})
    print(prm.get_data_dict())
    prm.single_earth_station.adjacent_ch_emissions = 123
    ses = prm.single_earth_station
    ses.adjacent_ch_emissions = ["Brazil", 2]
    # prm.imt.bs.antenna = ParametersAntenna(
    #     # type=
    # )
    print(prm.get_data_dict())
    # prm.single_earth_station.validate()
