from typing import Text, Any, Dict, List, Union
from copy import deepcopy
from ..data_controller import DataController, IdType, JSONItem


class DataAdapter:
    def __init__(self, resource: Union[Text, JSONItem], **kwargs: Any):
        if isinstance(resource, dict):
            data = deepcopy(resource)
            self.resource = data
        else:
            assert isinstance(resource, str)
            data = self.read_data()
            self.resource = resource
        self._controller = DataController(data, **kwargs)

    def read_data(self) -> Dict[Text, Any]:
        raise NotImplementedError

    def save_data(self) -> None:
        if isinstance(self.resource, dict):
            return
        raise NotImplementedError

    def execute_get_item_request(self, path: Text, id: IdType):
        return self._controller.get_item(self._split_paths(path), id)

    def execute_get_request(self, path: Text, **filters: Any):
        return self._controller.get_items(self._split_paths(path), **filters)

    def execute_post_request(self, path: Text, data: Any):
        return self._controller.add_item(self._split_paths(path), data)

    def execute_patch_request(self, path: Text, id: IdType,  data: Any):
        return self._controller.patch_item(self._split_paths(path), id, data)

    def execute_put_request(self, path: Text, id: IdType, data: Any):
        return self._controller.replace_item(self._split_paths(path), id, data)

    def execute_delete_request(self, path: Text, id: IdType):
        return self._controller.delete_item(self._split_paths(path), id)

    def get_data(self):
        return self._controller.data

    @ staticmethod
    def _split_paths(path: Text) -> List[Text]:
        path_as_list = [sub_path for sub_path in path.strip("/").split("/") if sub_path]
        return path_as_list
