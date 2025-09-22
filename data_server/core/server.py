import json
import logging
import multiprocessing
import sys
import time
import traceback
import typing as t
import warnings

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

import data_server.data_server_types as dt
from data_server.errors import DataServerError, ItemNotFoundError

URL_SEPARATOR = '/'


class Server:
    def __init__(
        self,
        request_handler: dt.RequestHandler,
        *,
        url_path_prefix: str = '',
        host: str = '127.0.0.1',
        disable_stdin: t.Optional[bool] = None,
        disable_logs: t.Optional[bool] = None,
        port: int = 5000,
        reload_interval: int = 1,
        additional_headers: str = '',
        static_folder: t.Optional[str] = None,
        static_url_prefix: str = 'static',
        sleep_before_request: int = 0,
        extra_files: t.Optional[t.List[str]] = None,
    ) -> None:
        self.request_handler = request_handler
        self._werkzeug_logger = logging.getLogger('werkzeug')
        self.url_path_prefix = url_path_prefix
        self.host = host
        self.port = port
        self.reload_interval = reload_interval
        self.static_folder = static_folder
        self.static_url_folder = static_url_prefix
        self.extra_files = extra_files or []
        self.stdin_handle: t.Optional[t.TextIO] = sys.stdin
        self.server_process: t.Optional[multiprocessing.Process] = None
        self._initial_log_level = self._werkzeug_logger.level
        try:
            self.additional_headers = self._parse_additional_headers(additional_headers)
        except Exception as e:
            warnings.warn(f'Failed to parse headers {e.args}', stacklevel=1)
            self.additional_headers = {}
        self.sleep_before_request = sleep_before_request
        if disable_stdin:
            # needed for werkzeug , to spin the server in a subprocess
            self.stdin_handle = None
        if disable_logs:
            self._werkzeug_logger.setLevel(logging.ERROR)

    def _parse_additional_headers(self, headers_as_text: str) -> t.Dict[str, str]:
        if not headers_as_text:
            return {}
        headers_as_list = [header_item for header_item in headers_as_text.split(';') if header_item]
        all_headers = {}
        for header_item in headers_as_list:
            key, value = map(str.strip, header_item.split(':'))
            all_headers[key] = value
        return all_headers

    def _handle_error_response(self, exception: Exception) -> t.Tuple[dt.JSONItem, int, dt.RequestHeaders]:
        def construct_error_response(message: str, code: int, details: t.Any) -> dt.JSONItem:
            return {'error': {'description': message, 'code': code, 'details': details}}

        if isinstance(exception, DataServerError):
            return (
                construct_error_response(exception.description, exception.code, ', '.join(map(str, exception.args))),
                exception.code,
                {},
            )
        traceback.print_exception(type(exception), exception, exception.__traceback__)
        return construct_error_response(', '.join(map(str, exception.args)), 500, None), 500, {}

    def _handle_options_request(self) -> t.Tuple[str, int, dt.RequestHeaders]:
        headers = self._update_headers(
            {
                'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
                'Access-Control-Allow-Origin': '*',
            }
        )
        return '', 200, headers

    def _encode_response_content(self, content: t.Any) -> str:
        return json.dumps(content)

    @staticmethod
    def strip_url_path_prefix(path: str, prefix: str) -> str:
        if not prefix:
            return path
        path = path.strip(URL_SEPARATOR)
        prefix = prefix.strip(URL_SEPARATOR)
        if not path.startswith(prefix):
            raise ItemNotFoundError('url cannot be resolved, check if prefix was added correctly')
        return path[len(prefix) :]

    def _handle_request(self, request: Request) -> t.Tuple[str, int, dt.RequestHeaders]:
        if request.method.upper() == dt.HTTPMethod.OPTIONS:
            return self._handle_options_request()

        query_parameters_as_dict = request.args
        request_data = request.json if request.is_json else request.get_data(as_text=True)
        url = self.strip_url_path_prefix(request.path, self.url_path_prefix)
        try:
            response_content = self.request_handler(
                request.method, url, query_parameters_as_dict, t.cast(dt.JSONItem, request_data)
            )
        except Exception as e:
            response_content, code, headers = self._handle_error_response(e)
            return self._encode_response_content(response_content), code, headers

        method = request.method.upper()
        if method == dt.HTTPMethod.POST:
            status_code = 201
        elif method == dt.HTTPMethod.DELETE and not response_content:
            status_code = 204
            response_content = ''
        else:
            status_code = 200

        return self._encode_response_content(response_content), status_code, {}

    def _update_headers(self, headers: dt.RequestHeaders) -> dt.RequestHeaders:
        headers.update({'Access-Control-Allow-Origin': '*'})
        headers.update(self.additional_headers)
        return headers

    def __call__(self, environ: t.Any, start_response: t.Any) -> t.Any:
        request = Request(environ)
        response_content, status_code, headers = self._handle_request(request)
        headers = self._update_headers(headers)
        response = Response(
            response_content,
            status=status_code,
            headers=headers,
            mimetype='application/json' if response_content else None,
        )
        if self.sleep_before_request:
            time.sleep(self.sleep_before_request / 1000)
        return response(environ, start_response)

    def _run(self) -> None:
        run_simple(
            self.host,
            self.port,
            self,
            use_reloader=False,
            reloader_interval=self.reload_interval,
            extra_files=self.extra_files,
        )

    def run(self) -> None:
        # self.server_process = multiprocessing.Process(target=self._run)
        # self.server_process.start()
        # self.server_process.join()
        self._run()

    def shutdown(self) -> None:
        # if self.server_process is None:
        #     raise RuntimeError('Server is not started') from None
        # self.server_process.terminate()
        self._werkzeug_logger.setLevel(self._initial_log_level)
