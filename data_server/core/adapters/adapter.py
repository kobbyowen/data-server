import typing as t
from copy import deepcopy
from functools import lru_cache

from data_server.core.data_controller import DataController
import data_server.typing as dt


class DataAdapter:
    def __init__(self, resource: t.Union[t.Text, dt.JSONItem], **kwargs: t.Any):
        if isinstance(resource, dict):
            data = deepcopy(resource)
            self.resource = ""
        else:
            assert isinstance(resource, str)
            self.resource = resource
            data = self.read_data()
        self._controller = DataController(data, **kwargs)
        self._url_data = self._get_url_data()

    def read_data(self) -> t.Dict[t.Text, t.Any]:
        raise NotImplementedError

    def save_data(self) -> None:
        raise NotImplementedError

    def execute_get_item_request(self, path: t.Text, id: dt.IdType) -> dt.JSONItem:
        return self._controller.get_item(self._split_paths(path), id)

    def execute_get_request(self, path: t.Text, **filters: t.Text) -> dt.JSONItems:
        return self._controller.get_items(self._split_paths(path), **filters)

    def execute_post_request(self, path: t.Text, data: t.Any) -> dt.JSONItem:
        return self._controller.add_item(self._split_paths(path), data)

    def execute_patch_request(self, path: t.Text, id: dt.IdType,  data: t.Any) -> dt.JSONItem:
        return self._controller.patch_item(self._split_paths(path), id, data)

    def execute_put_request(self, path: t.Text, id: dt.IdType, data: t.Any) -> dt.JSONItem:
        return self._controller.replace_item(self._split_paths(path), id, data)

    def execute_delete_request(self, path: t.Text, id: dt.IdType) -> None:
        return self._controller.delete_item(self._split_paths(path), id)

    def get_data(self) -> dt.JSONItem:
        return self._controller.data

    @lru_cache(128)
    def get_urls(self) -> t.List[t.Text]:
        return [item[0] for item in self._url_data]

    def get_url_data(self) -> t.List[t.Tuple[t.Text, type]]:
        return self._url_data

    def _get_url_data(self) -> t.List[t.Tuple[t.Text, type]]:
        urls: t.List[t.Tuple[t.Text, type]] = []

        def get_url_helper(data: dt.JSONItem, accumulated_path: t.Text = "") -> None:
            for key, value in data.items():
                new_path = f"{accumulated_path}/{key}"
                if isinstance(value, list):
                    urls.append((new_path, list))
                if isinstance(value, dict):
                    urls.append((new_path, dict))
                    get_url_helper(value, new_path)

        get_url_helper(self.get_data())
        return urls

    @staticmethod
    def _split_paths(path: t.Text) -> t.List[t.Text]:
        path_as_list = [sub_path for sub_path in path.strip("/").split("/") if sub_path]
        return path_as_list
