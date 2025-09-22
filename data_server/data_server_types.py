import typing as t
from enum import Enum

JSONItem = t.Dict[str, t.Any]

JSONItems = t.List[JSONItem]

JSONResult = t.Union[JSONItems, JSONItem]

FilterParams = t.Dict[str, t.Any]

IdType = t.Union[str, int]

ItemPath = t.List[str]

ResponseHeaders = t.Dict[str, str]

RequestHeaders = t.Dict[str, str]

RouterResponse = t.Union[JSONItem, JSONItems]

RequestHandler = t.Callable[[str, str, t.Optional[RequestHeaders], t.Optional[JSONItem]], RouterResponse]


class ResourceType(str, Enum):
    JSON_FILE = 'json'
    CSV_FILE = 'csv'
    PLAIN_DICT = 'dict'


class HTTPMethod(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PATCH = 'PATCH'


class SortOrder(str, Enum):
    ASC = 'asc'
    DESC = 'desc'
