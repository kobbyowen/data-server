import typing as t
from enum import Enum

JSONItem = t.Dict[t.Text, t.Any]

JSONItems = t.List[JSONItem]

JSONResult = t.Union[JSONItems, JSONItem]

FilterParams = t.Dict[t.Text, t.Any]

IdType = t.Union[t.Text, int]

ItemPath = t.List[t.Text]

ReponseHeaders = t.Dict[t.Text, t.Text]

RouterResponse = t.Union[JSONItem, JSONItems]


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class RouterParameters(t.TypedDict):
    method: t.Text
    url: t.Text
    query_parameters: t.Optional[t.Dict[t.Text, t.Text]]
    data: t.Optional[JSONItem]
