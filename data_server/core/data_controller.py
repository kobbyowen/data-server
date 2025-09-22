import typing as t
import random
from functools import reduce
from datetime import datetime
from uuid import uuid4

from data_server.errors import ItemNotFoundError, DuplicateIDFound, DataControllerError
import data_server.data_server_types as dt


class DataController:
    def __init__(
        self,
        data: t.Dict[str, t.Any],
        *,
        id_name: str = "id",
        fix: bool = False,
        sort_key_param_name: str = "sort_by",
        order_param_name: str = "order",
        page_param_name: str = "page",
        size_param_name: str = "size",
        default_page_size: int = 10,
        autogenerate_id: bool = False,
        use_timestamps: bool = False,
        created_at_key_name: str = "created_at",
        updated_at_key_name: str = "updated_at"
    ):
        """
        Initializes a data controller class. DataController is an abstraction that allows querying and modifying data
        which is loaded as a dictionary.
        """
        assert isinstance(data, dict), f"data must be of type dict not {type(data)}"
        self.data = data
        self.id_name = id_name
        self.sort_key_param_name = sort_key_param_name
        self.order_param_name = order_param_name
        self.page_param_name = page_param_name
        self.size_param_name = size_param_name
        self.default_page_size = default_page_size
        self.auto_generate_id = autogenerate_id
        self.use_timestamps = use_timestamps
        self.created_at_key_name = created_at_key_name
        self.updated_at_key_name = updated_at_key_name
        self.id_type = self._get_id_type(data)
        self.fix = fix
        if self.fix:
            self._fix_data(self.data)

    def get_items(self, path: dt.ItemPath, **filters: t.Any) -> dt.JSONItems:
        items = self._get_item_by_path_only(path)
        assert isinstance(items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        try:
            return self._get_items(items, **filters)
        except ValueError as e:
            raise DataControllerError(description=e.args[0], code=400)

    def get_item(self, path: dt.ItemPath, id: dt.IdType) -> dt.JSONItem:
        return self._get_item_by_path_and_id(path, id)

    def delete_item(self, path: dt.ItemPath, id: dt.IdType) -> None:
        parent, index = self._get_item_parent_and_index(path, id)
        del parent[index]

    def patch_item(self, path: dt.ItemPath, id: dt.IdType, new_data: dt.JSONItem) -> dt.JSONItem:
        if self.id_name in new_data:
            raise ValueError("id cannot be patched")
        parent, index = self._get_item_parent_and_index(path, id)
        parent[index].update(new_data)
        return self._update_timestamps(parent[index])

    def replace_item(self, path: dt.ItemPath, id: dt.IdType, new_data: dt.JSONItem) -> dt.JSONItem:
        if self.id_name in new_data and new_data[self.id_name] != id:
            raise ValueError("id cannot be replaced")
        parent, index = self._get_item_parent_and_index(path, id)
        parent[index] = {**new_data, self.id_name: id}
        return self._update_timestamps(parent[index])

    def add_item(self, path: dt.ItemPath, new_data: dt.JSONItem) -> dt.JSONItem:
        items = self._get_item_by_path_only(path)
        assert isinstance(items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        data = new_data.copy()
        if not self.auto_generate_id and self.id_name in data:
            if any(item[self.id_name] == data[self.id_name] for item in items):
                raise DuplicateIDFound(f"an item exists with same id {data[self.id_name]}", code=409)
        if self.auto_generate_id and self.id_name not in data:
            data[self.id_name] = self._autogenerate_id(items)
        data = self._add_timestamps(data)
        items.append(data)
        return data

    def _get_id_type(self, data: dt.JSONItem) -> t.Optional[type]:
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
    def _filter_items(data: dt.JSONItems, **filters: t.Any) -> dt.JSONItems:
        return [
            item for item in data
            if all(item.get(key) == value for key, value in filters.items())
        ]

    def _fix_data_item(self, data: dt.JSONItem, list_data: dt.JSONItems) -> dt.JSONItem:
        data[self.id_name] = self._autogenerate_id(list_data=list_data)
        self._add_timestamps(data, remove_stamps=True)
        return data

    def _fix_data(self, data: dt.JSONItem) -> None:
        for value in data.values():
            if isinstance(value, list):
                for item in value:
                    self._fix_data_item(item, value)
            elif isinstance(value, dict):
                self._fix_data(value)

    def _get_item_parent_and_index(self, path: dt.ItemPath, id: dt.IdType) -> t.Tuple[dt.JSONItems, int]:
        items = self._get_item_by_path_only(path)
        assert isinstance(items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        try:
            item_index = next(i for i, v in enumerate(items) if v[self.id_name] == id)
        except StopIteration:
            raise ItemNotFoundError(f"item with id {id} could not be resolved from path {path!r}")
        return items, item_index

    def _get_item_by_path_only(self, path: dt.ItemPath) -> dt.JSONResult:
        try:
            return reduce(lambda prev, cur: t.cast(dt.JSONItem, prev[cur]), path, self.data)
        except KeyError:
            raise ItemNotFoundError(f"{path} could not be resolved in data")

    def _get_item_by_path_and_id(self, path: dt.ItemPath, id: dt.IdType) -> dt.JSONItem:
        items = self._get_item_by_path_only(path)
        assert isinstance(items, list), f"Expected value for {path!r} to be a list, got {items} instead"
        filtered = [x for x in items if x[self.id_name] == id]
        if not filtered:
            raise ItemNotFoundError(f"No item with id {id} exists")
        return filtered[0]

    def _update_timestamps(self, item: dt.JSONItem) -> dt.JSONItem:
        if self.use_timestamps:
            item[self.updated_at_key_name] = datetime.now().isoformat()
        return item

    def _add_timestamps(
        self,
        item: dt.JSONItem,
        update_updated_at: bool = False,
        remove_stamps: bool = False
    ) -> dt.JSONItem:
        if not self.use_timestamps and remove_stamps:
            item.pop(self.created_at_key_name, None)
            item.pop(self.updated_at_key_name, None)
            return item
        if self.created_at_key_name not in item:
            item[self.created_at_key_name] = datetime.now().isoformat()
        if self.updated_at_key_name not in item:
            item[self.updated_at_key_name] = None if update_updated_at else datetime.now().isoformat()
        return item

    def _get_items(self, data: dt.JSONItems, **filters: t.Any) -> dt.JSONItems:
        sort_key = filters.pop(self.sort_key_param_name, self.id_name)
        order = filters.pop(self.order_param_name, dt.SortOrder.ASC.value)
        order_enum = dt.SortOrder.ASC if order.lower() == dt.SortOrder.ASC.value else dt.SortOrder.DESC
        page = int(filters.pop(self.page_param_name, 0))
        if page < 0:
            raise DataControllerError(
                f"{self.page_param_name!r} should be a non negative integer, got {page}", 400)
        size = int(filters.pop(self.size_param_name, self.default_page_size))
        if size < 0:
            raise DataControllerError(
                f"{self.size_param_name!r} should be a non negative integer, got {size}", 400)
        filtered = self._filter_items(data, **filters)
        filtered.sort(
            key=lambda item: item.get(sort_key, list(self.data.keys())[0]),
            reverse=order_enum == dt.SortOrder.DESC
        )
        start_index = page * size
        end_index = start_index + size
        return filtered[start_index:end_index]

    def _autogenerate_id(self, list_data: dt.JSONItems, *, use_random: bool = False) -> t.Union[str, int]:
        exclude = [x.get(self.id_name) for x in list_data if x.get(self.id_name) is not None]
        data_length = len(list_data)
        if self.id_type is int:
            if use_random:
                random_int = random.randint(0, 100_000_000)
                while random_int in exclude:
                    random_int = random.randint(0, 100_000_000)
                return random_int
            for i in range(1, data_length):
                if i not in exclude:
                    return i
            count = 0
            while data_length + count in exclude:
                count += 1
            return data_length + count
        string_id = str(uuid4())
        while string_id in exclude:
            string_id = str(uuid4())
        return string_id
