import typing as t
import json
import time
import warnings
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from data_server.errors import DataServerError, ItemNotFoundError
import data_server.typing as dt

URL_SEPARATOR = "/"


class Server:
    def __init__(self, request_handler: dt.RequestHandler, *, url_path_prefix: t.Text = "",
                 host: t.Text = "127.0.0.1", port: int = 5000, reload_interval: int = 1,
                 static_folder: t.Optional[t.Text] = None, static_url_prefix: t.Text = "static",
                 additional_headers: t.Text = "", sleep_before_request: int = 0) -> None:
        self.request_handler = request_handler
        self.url_path_prefix = url_path_prefix
        self.host = host
        self.port = port
        self.reload_interval = reload_interval
        self.static_folder = static_folder
        self.static_url_folder = static_url_prefix
        try:
            self.additional_headers = self._parse_additional_headers(additional_headers)
        except Exception as e:
            warnings.warn(f"Failed to parse headers {e.args}")
            self.additional_headers = {}
        self.sleep_before_request = sleep_before_request

    def _parse_additional_headers(self, headers_as_text: t.Text) -> t.Dict[t.Text, t.Text]:
        if not headers_as_text:
            return {}
        headers_as_list = [header_item for header_item in headers_as_text.split(";") if header_item]
        all_headers = {}
        for header_item in headers_as_list:
            key, value = map(str.strip, header_item.split(":"))
            all_headers[key] = value
        return all_headers

    def _handle_error_response(self, exception: Exception) -> t.Tuple[dt.JSONItem, int, dt.RequestHeaders]:
        def construct_erorr_response(message: t.Text, code: int, details: t.Any) -> dt.JSONItem: return (
            {"error": {"description": message, "code": code, "details": details}})

        if isinstance(exception, DataServerError):
            return construct_erorr_response(exception.description,
                                            exception.code, ", ".join(map(str, exception.args))), exception.code, {}
        return construct_erorr_response(", ".join(map(str, exception.args)), 500, None), 500, {}

    def _handle_options_request(self) -> t.Tuple[t.Text, int, dt.RequestHeaders]:
        headers = self._update_headers(
            {"Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
             "Access-Control-Allow-Origin": "*"})
        return "", 200, headers

    def _encode_response_content(self, content: t.Any) -> t.Text:
        return json.dumps(content)

    @staticmethod
    def strip_url_path_prefix(path: t.Text, prefix: t.Text) -> t.Text:
        if not prefix:
            return path
        path = path.strip(URL_SEPARATOR)
        prefix = prefix.strip(URL_SEPARATOR)
        if not path.startswith(prefix):
            raise ItemNotFoundError("url cannot be resolved, check if prefix was added correctly")
        return path[len(prefix):]

    def _handle_request(self, request: Request) -> t.Tuple[t.Text, int, dt.RequestHeaders]:
        if request.method.upper() == dt.HTTPMethod.OPTIONS:
            return self._handle_options_request()

        query_parameters_as_dict = request.args
        request_data = request.json if request.is_json else request.get_data(as_text=True)
        url = self.strip_url_path_prefix(request.path, self.url_path_prefix)
        try:
            response_content = self.request_handler(request.method, url,
                                                    query_parameters_as_dict, t.cast(dt.JSONItem, request_data))
        except Exception as e:
            response_content, code, headers = self._handle_error_response(e)
            return self._encode_response_content(response_content), code, headers
        return self._encode_response_content(response_content), 200, {}

    def _update_headers(self, headers: dt.RequestHeaders, use_cors: bool = True) -> dt.RequestHeaders:
        if use_cors:
            headers.update({"Access-Control-Allow-Origin": "*"})
        headers.update(self.additional_headers)
        return headers

    def __call__(self, environ: t.Any, start_response: t.Any) -> t.Any:
        request = Request(environ)
        response_content, status_code, headers = self._handle_request(request)
        headers = self._update_headers(headers)
        response = Response(response_content, status=status_code, headers=headers,
                            mimetype="application/json" if response_content else None)
        if self.sleep_before_request:
            time.sleep(self.sleep_before_request / 1000)
        return response(environ, start_response)

    def run(self) -> None:
        run_simple(self.host, self.port, self, use_reloader=True, reloader_interval=self.reload_interval)
