import typing as t
from copy import deepcopy

import data_server.data_server_types as dt
from data_server.core.data_controller import DataController


class DataAdapter:
    def __init__(self, resource: t.Union[str, dt.JSONItem], **kwargs: t.Any):
        if isinstance(resource, dict):
            data = deepcopy(resource)
            self.resource = ''
        else:
            assert isinstance(resource, str)
            self.resource = resource
            data = self.read_data()
        self._controller = DataController(data, **kwargs)
        self._url_data = self._get_url_data()

    def read_data(self) -> t.Dict[str, t.Any]:
        raise NotImplementedError

    def save_data(self) -> None:
        raise NotImplementedError

    def execute_get_item_request(self, path: str, id: dt.IdType) -> dt.JSONItem:
        return self._controller.get_item(self._split_paths(path), id)

    def execute_get_request(self, path: str, **filters: str) -> dt.JSONItems:
        return self._controller.get_items(self._split_paths(path), **filters)

    def execute_post_request(self, path: str, data: t.Any) -> dt.JSONItem:
        return self._controller.add_item(self._split_paths(path), data)

    def execute_patch_request(self, path: str, id: dt.IdType, data: t.Any) -> dt.JSONItem:
        return self._controller.patch_item(self._split_paths(path), id, data)

    def execute_put_request(self, path: str, id: dt.IdType, data: t.Any) -> dt.JSONItem:
        return self._controller.replace_item(self._split_paths(path), id, data)

    def execute_delete_request(self, path: str, id: dt.IdType) -> None:
        return self._controller.delete_item(self._split_paths(path), id)

    def get_data(self) -> dt.JSONItem:
        return self._controller.data

    def get_urls(self) -> t.List[str]:
        return [item[0] for item in self._url_data]

    def get_url_data(self) -> t.List[t.Tuple[str, type]]:
        return self._url_data

    def _get_url_data(self) -> t.List[t.Tuple[str, type]]:
        urls: t.List[t.Tuple[str, type]] = []

        def get_url_helper(data: dt.JSONItem, accumulated_path: str = '') -> None:
            for key, value in data.items():
                new_path = f'{accumulated_path}/{key}'
                if isinstance(value, list):
                    urls.append((new_path, list))
                if isinstance(value, dict):
                    urls.append((new_path, dict))
                    get_url_helper(value, new_path)

        get_url_helper(self.get_data())
        return urls

    @staticmethod
    def _split_paths(path: str) -> t.List[str]:
        path_as_list = [sub_path for sub_path in path.strip('/').split('/') if sub_path]
        return path_as_list
