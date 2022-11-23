from typing import Dict, Text, Any, List
from enum import StrEnum
from functools import lru_cache, reduce

JSONItem = Dict[Text, Any]
JSONItems = List[JSONItem]
FilterParams = Dict[Text, Any]
IdType = Text | int
ItemPath = List[Text]


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class DataController:
    def __init__(self, data: Dict[Text, Any], *, id_name: str = "id", sort_key_param_name="sort_key",
                 order_param_name="order", page_param_name="page", size_param_name="size", default_page_size=10,
                 autogenerate_id=False,
                 use_timestamps=False, created_at_key_name="created_at", updated_at_key_name="updated_at"):
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

    def _get_id_type(self):
        pass

    @lru_cache
    def filter_data(self, data: JSONItems, **filters: FilterParams) -> JSONItems:
        new_data = []
        for item in data:
            for key, value in filters.items():
                if key in data and item[key] != value:
                    break
            else:
                new_data.append(item)
        return new_data

    def get_data(self, data: JSONItems, **filters: FilterParams):
        sort_key = filters.pop(self.sort_key_param_name, self.id_name)
        self.order = filters.pop(self.order_param_name, SortOrder.ASC.value)
        self.order = SortOrder.ASC if self.order.lower == SortOrder.ASC.value else SortOrder.DESC
        self.page = filters.pop(self.page_param_name, 0)
        self.size = filters.pop(self.page_param_name, self.default_page_size)
        new_data = self.filter_data(data, **filters)
        new_data.sort(key=lambda item: item[sort_key], reverse=self.order == SortOrder.DESC)
        start_index = self.page * self.size
        end_index = start_index + self.size
        return new_data[start_index:end_index]

    def get_data_by_id(self, path: ItemPath, id: IdType):
        # allow KeyError if path cannot be found
        value = reduce(lambda prev, cur: prev[cur], path, self.data)
        items = list(filter(lambda x: x[self.id_name] == id), value)
        # allow IndexError if no item is found
        return items[0]

    def remove_data_by_id(self, path: ItemPath, id: IdType):
        pass

    def patch_data_by_id(self, path: ItemPath, id: IdType):
        pass

    def replace_data_by_id(self, path: ItemPath, id: IdType):
        pass

    def add_data(self, path: ItemPath):
        pass
