import typing as t
from enum import Enum
from pathlib import Path
import data_server.typing as dt
from data_server.errors import ItemNotFoundError
from data_server.core.adapters.adapter import DataAdapter
from data_server.core.adapters.json_adapter import JSONAdapter
from data_server.core.adapters.csv_adapter import CsvAdapter


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


URL_SEPARATOR = "/"


class DataRouter:
    def __init__(self, resource: t.Union[t.Text, dt.JSONItem], **kwargs: t.Any) -> None:
        self.resource = resource
        if isinstance(resource, dict):
            self.resource_type = ResourceType.PLAIN_DICT
            self.data_adapter = DataAdapter(resource, **kwargs)
        else:
            self.resource_type = self._detect_resource_type(resource)
            self.data_adapter = self._create_data_adapter(self.resource_type, t.cast(str, self.resource), **kwargs)

    @staticmethod
    def _detect_resource_type(resource: t.Text) -> ResourceType:
        extension = Path(resource).suffix
        if extension == ".json":
            return ResourceType.JSON_FILE
        if extension == ".csv":
            return ResourceType.CSV_FILE
        return ResourceType.JSON_FILE

    @staticmethod
    def _create_data_adapter(resource_type: ResourceType, resource: t.Text, **kwargs: t.Any) -> DataAdapter:
        if resource_type == ResourceType.CSV_FILE:
            return CsvAdapter(resource, **kwargs)
        # default to json adapter
        return JSONAdapter(resource, **kwargs)

    def _parse_url(self, url: t.Text) -> t.Tuple[t.Text, t.Optional[dt.IdType]]:
        all_urls = self.data_adapter.get_urls()
        if url in all_urls:
            return url, None
        *url_base, resource_id = url.split(URL_SEPARATOR)
        base_url = URL_SEPARATOR + URL_SEPARATOR.join(url_base).strip(URL_SEPARATOR)
        if base_url not in all_urls:
            raise ItemNotFoundError(f"{url!r} not found")
        id_type = self.data_adapter._controller.id_type or str
        return base_url, id_type(resource_id)

    def _handle_http_get_request(self, base_url: t.Text, resource_id: t.Optional[dt.IdType],
                                 **query_parameters: t.Text) -> dt.RouterResponse:
        if resource_id is None:
            return self.data_adapter.execute_get_request(base_url, **query_parameters)
        else:
            return self.data_adapter.execute_get_item_request(base_url, resource_id)

    def _handle_http_update_request(self, method: t.Text, base_url: t.Text, resource_id: dt.IdType,
                                    data: dt.JSONItem) -> dt.RouterResponse:
        request_handler = {
            HTTPMethod.PATCH.value: self.data_adapter.execute_patch_request,
            HTTPMethod.PUT.value: self.data_adapter.execute_put_request
        }[method]
        return request_handler(base_url, resource_id, data)

    def _handle_http_request(self, method: t.Text, url: t.Text, *,
                             query_parameters: t.Optional[t.Dict[t.Text, t.Text]] = None,
                             data: t.Optional[dt.JSONItem] = None) -> dt.RouterResponse:
        query_parameters = query_parameters or {}
        data = data or {}
        base_url, resource_id = self._parse_url(url)
        print(base_url, resource_id)
        if method == HTTPMethod.GET:
            return self._handle_http_get_request(base_url, resource_id, **query_parameters)
        if method == HTTPMethod.POST:
            return self.data_adapter.execute_post_request(base_url, data)
        if method == HTTPMethod.PATCH or method == HTTPMethod.PUT:
            assert resource_id is not None
            return self._handle_http_update_request(method, base_url, resource_id, data)
        if method == HTTPMethod.DELETE:
            assert resource_id is not None
            self.data_adapter.execute_delete_request(base_url, resource_id)
            return {}
        raise ValueError(f"cannot handle request for method {method!r}")

    def __call__(self, *, method: t.Text, url: t.Text,
                 query_parameters: t.Optional[t.Dict[t.Text, t.Text]] = None,
                 data: t.Optional[dt.JSONItem] = None) -> dt.RouterResponse:
        method = method.upper()
        url = URL_SEPARATOR + url.strip(URL_SEPARATOR)
        method = method.upper()
        results = self._handle_http_request(method, url, query_parameters=query_parameters, data=data)
        return results
