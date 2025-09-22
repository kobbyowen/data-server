import subprocess
import json
from distutils import spawn
from random import randint
from datetime import datetime
from uuid import uuid4
import typing as t
from http.client import HTTPConnection
import data_server.data_server_types as dt


class Order(t.TypedDict):
    key: str
    orderName: str
    orderNumber: int
    createdAt: str


def command_exists(command: t.Text) -> bool:
    return spawn.find_executable(command) is not None


class ClientResponse(t.TypedDict):
    status: int
    reason: t.Text
    headers: dt.ResponseHeaders
    data: bytes
    json: t.Dict[t.Any, t.Any]


class TestServer:
    def __init__(
        self, port: int, server_file: t.Text = "tests/int/fixtures/server-data.json", **server_options
    ) -> None:
        self.process: t.Optional[subprocess.Popen[bytes]] = None
        self.server_file = server_file
        self.port = port
        self.id_name = server_options.get("id_name", "key")
        self.host = server_options.get("host", "0.0.0.0")
        self.additional_headers = server_options.get(
            "additional_headers", "x-server:integration-tests;x-test-header:value"
        )
        self.page_size = server_options.get("page_size", 5)
        self.page_param_name = server_options.get("page_param_name", "leaf")
        self.sort_param_name = server_options.get("sort_param_name", "sort_with")
        self.order_param_name = server_options.get("order_param_name", "data-order")
        self.size_param_name = server_options.get("size_param_name", "length")
        self.created_at_param_name = server_options.get("created_at_param_name", "createdAt")
        self.updated_at_param_name = server_options.get("updated_at_param_name", "updatedAt")
        self.auto_generate_id = server_options.get("auto_generate_id", True)
        self.use_timestamps = server_options.get("use_timestamps", True)
        self.url_path_prefix = server_options.get("url_path_prefix", "/api/v3")
        self.command = ""

    def run(self) -> None:
        python_command = "python" if command_exists("python") else "python3"
        self.command = f"{python_command} main.py {self.server_file} \
        --host=0.0.0.0  --port={self.port} --url-path-prefix={self.url_path_prefix} \
        --additional-headers='{self.additional_headers}' \
        --page-size={self.page_size} --page-param-name={self.page_param_name} --sort-param-name={self.sort_param_name} \
        --order-param-name={self.order_param_name} --size-param-name={self.size_param_name} \
        --created-at-key-name={self.created_at_param_name} --updated-at-key-name={self.updated_at_param_name} \
        --id-name={self.id_name} {'--auto-generate-ids=true' if self.auto_generate_id else '--auto-generate-ids=false'} \
        {'--use-timestamps=true' if self.use_timestamps else ''} --disable-stdin=true --disable-logs=True"
        self.process = subprocess.Popen(self.command, shell=True)

    def __del__(self):
        self.stop()

    def stop(self) -> None:
        if self.process:
            self.process.terminate()


class TestClient:
    def __init__(self, port: int) -> None:
        self.host = "127.0.0.1"
        self.port = port

    def _make_request(
        self,
        method: dt.HTTPMethod,
        url: t.Text,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        connection = HTTPConnection(f"{self.host}:{self.port}")
        body = None
        request_headers = headers.copy() if headers else {}

        if method in {dt.HTTPMethod.POST, dt.HTTPMethod.PUT, dt.HTTPMethod.PATCH, dt.HTTPMethod.DELETE} and data is not None:
            body = json.dumps(data).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        elif data is not None:
            body = json.dumps(data).encode("utf-8")

        connection.request(method.value, url, body=body, headers=request_headers)
        response = connection.getresponse()
        response_data = response.read()
        try:
            response_json_data = json.loads(response_data)
        except Exception:
            response_json_data = None
        return {
            "status": response.status,
            "reason": response.reason,
            "headers": dict(response.getheaders()),
            "data": response_data,
            "json": response_json_data,
        }

    def get(
        self,
        url: t.Text,
        *,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        return self._make_request(dt.HTTPMethod.GET, url, data, headers)

    def post(
        self,
        url: t.Text,
        *,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        return self._make_request(dt.HTTPMethod.POST, url, data, headers)

    def put(
        self,
        url: t.Text,
        *,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        return self._make_request(dt.HTTPMethod.PUT, url, data, headers)

    def patch(
        self,
        url: t.Text,
        *,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        return self._make_request(dt.HTTPMethod.PATCH, url, data, headers)

    def delete(
        self,
        url: t.Text,
        *,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        return self._make_request(dt.HTTPMethod.DELETE, url, data, headers)

    def request(
        self,
        method: t.Text,
        url: t.Text,
        *,
        data: t.Optional[t.Dict[t.Any, t.Any]] = None,
        headers: t.Optional[dt.RequestHeaders] = None,
    ) -> ClientResponse:
        return self._make_request(dt.HTTPMethod(method), url, data, headers)


def generate_order(
    *,
    id_name: t.Text = "id",
    id_type: type = int,
    add_timestamps: bool = True,
    created_at_key: t.Text = "createdAt",
    updated_at_key: t.Text = "updatedAt",
    **kwargs: t.Any,
) -> Order:
    random_number_upper_limit = 2**64
    order_data = {
        id_name: randint(0, random_number_upper_limit)
        if id_type is int
        else str(uuid4()),
        "orderName": f"order-{randint(0, random_number_upper_limit)}",
        "orderNumber": randint(0, random_number_upper_limit),
    }
    if add_timestamps:
        order_data[created_at_key] = str(datetime.now())
        order_data[updated_at_key] = None

    return t.cast(Order, {**order_data, **kwargs})
