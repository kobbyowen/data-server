import typing as t
from copy import deepcopy

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

    def read_data(self) -> t.Dict[t.Text, t.Any]:
        raise NotImplementedError

    def save_data(self) -> None:
        raise NotImplementedError

    def execute_get_item_request(self, path: t.Text, id: dt.IdType) -> dt.JSONItem:
        return self._controller.get_item(self._split_paths(path), id)

    def execute_get_request(self, path: t.Text, **filters: t.Any) -> dt.JSONItems:
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

    @staticmethod
    def _split_paths(path: t.Text) -> t.List[t.Text]:
        path_as_list = [sub_path for sub_path in path.strip("/").split("/") if sub_path]
        return path_as_list
