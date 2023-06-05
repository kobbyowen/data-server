import typing as t
from enum import Enum

JSONItem = t.Dict[t.Text, t.Any]

JSONItems = t.List[JSONItem]

JSONResult = t.Union[JSONItems, JSONItem]

FilterParams = t.Dict[t.Text, t.Any]

IdType = t.Union[t.Text, int]

ItemPath = t.List[t.Text]

ReponseHeaders = t.Dict[t.Text, t.Text]

RequestHeaders = t.Dict[t.Text, t.Text]

RouterResponse = t.Union[JSONItem, JSONItems]

RequestHandler = t.Callable[[t.Text, t.Text, t.Optional
                             [t.Dict[t.Text, t.Text]],
                             t.Optional[JSONItem]],
                            RouterResponse]


class ResourceType(str, Enum):
    JSON_FILE = "json"
    CSV_FILE = "csv"
    PLAIN_DICT = "dict"


class HTTPMethod(str, Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
