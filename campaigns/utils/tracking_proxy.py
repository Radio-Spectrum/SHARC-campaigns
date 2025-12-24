from typing import Any
from sharc.parameters.parameters import Parameters

class TrackingProxy:
    def __init__(self, obj: Any, data: dict = None, path: list = []):
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

        # full_path = f"{self._path}.{name}" if self._path else name
        full_path = self._path + [name] if self._path else [name]

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
                path=self._path + [name] if self._path else [name],
            )
            object.__setattr__(self, name, proxy)
            return proxy
        elif isinstance(attr, list):
            # wrap list items if needed
            wrapped_list = []
            for index, item in enumerate(attr):
                if self._is_trackable(item):
                    item_proxy = TrackingProxy(
                        item,
                        data=self._data,
                        # path=f"{self._path}.{name}[{index}]"
                        path=self._path + [name] + [index]
                        if self._path
                        else [name] + [index],
                    )
                    wrapped_list.append(item_proxy)
                else:
                    wrapped_list.append(item)
            object.__setattr__(self, name, wrapped_list)
            return wrapped_list
        return attr

    def get_data_dict(self):
        return self._data

    def _update_data(self, path, value):
        d = self._data
        for key in path[:-1]:
            if isinstance(d, list):  # we're traversing a list
                d = d[key]
                continue
            d = d.setdefault(key, {})
        d[path[-1]] = value


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
