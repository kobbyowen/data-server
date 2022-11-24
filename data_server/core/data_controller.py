from typing import Dict, Text, Any, List, Union, Tuple, Optional
from enum import Enum
from functools import reduce
from datetime import datetime
from uuid import uuid4

from data_server.errors import ItemNotFoundError

JSONItem = Dict[Text, Any]
JSONItems = List[JSONItem]
FilterParams = Dict[Text, Any]
IdType = Union[Text, int]
ItemPath = List[Text]


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class DataController:
    def __init__(self, data: Dict[Text, Any], *, id_name: Text = "id",
                 sort_key_param_name: Text = "sort_by", order_param_name: Text = "order",
                 page_param_name: Text = "page", size_param_name: Text = "size",
                 default_page_size: int = 10, autogenerate_id: bool = False, use_timestamps: bool = False,
                 created_at_key_name: Text = "created_at", updated_at_key_name: Text = "updated_at"):
        self.data = data
        self.id_name = id_name
        self.sort_key_param_name = sort_key_param_name
        self.order_param_name = order_param_name
        self.page_param_name = page_param_name
        self.size_param_name = size_param_name
        self.default_page_size = default_page_size
        self.auto_generate_id = autogenerate_id
        self.use_timestamps = use_timestamps
        self.created_at_timestamp_name = created_at_key_name
        self.updated_at_key_name = updated_at_key_name
        self.id_type = self._get_id_type(data)

    def _get_items(self, data: JSONItems, **filters: Any):
        sort_key = filters.pop(self.sort_key_param_name, self.id_name)
        self.order = filters.pop(
            self.order_param_name, SortOrder.ASC.value)
        self.order = SortOrder.ASC if self.order.lower(
        ) == SortOrder.ASC.value else SortOrder.DESC
        self.page = filters.pop(self.page_param_name, 0)
        self.size = filters.pop(self.size_param_name, self.default_page_size)
        new_data = self._filter_items(data, **filters)
        new_data.sort(
            key=lambda item: item[sort_key], reverse=self.order == SortOrder.DESC)
        start_index = self.page * self.size
        end_index = start_index + self.size
        return new_data[start_index:end_index]

    def get_items(self, path: ItemPath, **filters: Any) -> JSONItems:
        items = self._get_item_by_path_only(path)
        assert isinstance(
            items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        return self._get_items(items, **filters)

    def get_item(self, path: ItemPath, id: IdType) -> JSONItem:
        return self._get_item_by_path_and_id(path, id)

    def delete_item(self, path: ItemPath, id: IdType) -> None:
        parent, index = self._get_item_parent_and_index(path, id)
        del parent[index]

    def patch_item(self, path: ItemPath, id: IdType, new_data: JSONItem) -> JSONItem:
        parent, index = self._get_item_parent_and_index(path, id)
        parent[index].update(new_data)
        return self._update_timestamps(parent[index])

    def replace_item(self, path: ItemPath, id: IdType, new_data: JSONItem) -> JSONItem:
        parent, index = self._get_item_parent_and_index(path, id)
        parent[index] = new_data
        return self._update_timestamps(parent[index])

    def add_item(self, path: ItemPath, new_data: JSONItem) -> JSONItem:
        items = self._get_item_by_path_only(path)
        assert isinstance(
            items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        data = new_data.copy()
        if self.auto_generate_id and self.id_name not in data:
            data[self.id_name] = self._autogenerate_id(len(items))
        data = self._add_timestamps(data)
        items.append(data)
        return data

    def _get_id_type(self, data: JSONItem) -> Optional[type]:
        for key, value in data.items():
            if key == self.id_name:
                return type(value)
            if isinstance(value, list):
                for item in value:
                    return self._get_id_type(item)
            if isinstance(value, dict):
                return self._get_id_type(value)
        return None

    @staticmethod
    def _filter_items(data: JSONItems, **filters: Any) -> JSONItems:
        new_data = []
        for item in data:
            for key, value in filters.items():
                if key in item and item[key] != value:
                    break
            else:
                new_data.append(item)
        return new_data

    def _get_item_parent_and_index(self, path: ItemPath, id: IdType) -> Tuple[JSONItems, int]:
        items = self._get_item_by_path_only(path)
        assert isinstance(
            items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        try:
            item_index = next(i for i, v in enumerate(items)
                              if v[self.id_name] == id)
        except StopIteration:
            raise ItemNotFoundError("item with id {id} could not be resolved from path {path!r}")
        return items, item_index

    def _get_item_by_path_only(
            self, path: ItemPath) -> Union[JSONItem, JSONItems]:
        try:
            value = reduce(lambda prev, cur: prev[cur], path, self.data)
            return value
        except KeyError:
            raise ItemNotFoundError(f"{path} could not be resloved in data")

    def _get_item_by_path_and_id(self, path: ItemPath, id: IdType) -> JSONItem:
        items = self._get_item_by_path_only(path)
        assert isinstance(
            items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        items = list(filter(lambda x: x[self.id_name] == id, items))
        try:
            return items[0]
        except IndexError:
            raise ItemNotFoundError(f"No item with id {id} exists")

    def _update_timestamps(self, item: JSONItem) -> JSONItem:
        if not self.use_timestamps:
            return item
        item[self.updated_at_key_name] = datetime.now().isoformat()
        return item

    def _add_timestamps(self, item: JSONItem, update_updated_at: bool = False) -> JSONItem:
        if not self.use_timestamps:
            return item
        item[self.created_at_timestamp_name] = datetime.now().isoformat()
        item[self.updated_at_key_name] = None if update_updated_at else datetime.now().isoformat()
        return item

    def _autogenerate_id(self, data_length: int) -> Union[Text, int]:
        if self.id_type is int:
            return data_length + 1
        return str(uuid4())
