from unittest import TestCase
from unittest.mock import patch, MagicMock
import json
from io import BytesIO

from werkzeug.test import create_environ

from data_server.core.server import Server
from data_server.errors import ItemNotFoundError


def default_handler(method, url, args, data): return {"url": url,
                                                      "method": method, "args": dict(args), "data": dict(data)}


class TestServerInitialization(TestCase):
    def test_initialization_with_valid_headers(self):
        server = Server(default_handler, additional_headers="x-range:20;x-limit:30 ; x-hold:50")
        self.assertDictEqual(server.additional_headers, {"x-range": "20", "x-limit": "30", "x-hold": "50"})

    @patch("warnings.warn")
    def test_initialization_with_invalid_headers(self, mocked_warning:  MagicMock):
        server = Server(default_handler, additional_headers="header")
        self.assertDictEqual(server.additional_headers, {})
        self.assertTrue(mocked_warning.called)

    def test_initialization_with_empty_headers(self):
        server = Server(default_handler, additional_headers="")
        self.assertDictEqual(server.additional_headers, {})

    @patch("data_server.core.server.run_simple")
    def test_run(self, mocked_run: MagicMock):
        server = Server(default_handler, additional_headers="", host="localhost", port=6000, reload_interval=20)
        server.run()
        mocked_run.assert_called_with("localhost", 6000, server, use_reloader=True, reloader_interval=20)


class TestRequesthandling(TestCase):
    def setUp(self) -> None:
        response_adapter = patch("data_server.core.server.Response")
        self.response_adapter_mock = response_adapter.start()
        self.response_adapter_mocked_instance = self.response_adapter_mock.return_value
        self.plain_environ = create_environ(path="/books/20", method="GET")
        self.plain_environ_with_url_prefix = create_environ(path="/api/v3.1/books/20", method="GET")
        self.options_environ = create_environ(path="/books/20", method="OPTIONS")
        self.fake_start_response = lambda status, header: {"status": status, "header": header}
        self.data = {"name": "A Book"}
        input_bytes = json.dumps(self.data).encode()
        self.environ_with_data = create_environ(path="/books/20", method="POST", mimetype="application/json",
                                                content_length=len(input_bytes),
                                                input_stream=BytesIO(input_bytes))
        self.xml_data = "<book><name>A Book</name></book>"
        self.environ_with_xml_data = create_environ(path="/books/20", method="POST", mimetype="application/xml",
                                                    content_length=len(self.xml_data.encode()),
                                                    input_stream=BytesIO(self.xml_data.encode()))
        super().setUp()

    def test_request_with_url_prefix(self):
        server = Server(default_handler, url_path_prefix="/api/v3.1/")
        server(self.plain_environ_with_url_prefix, self.fake_start_response)
        target_response = json.dumps(default_handler("GET", "/books/20", {}, {}))
        self.assertTrue(self.response_adapter_mock.called)
        self.response_adapter_mock.assert_called_with(target_response, status=200, headers={
                                                      'Access-Control-Allow-Origin': '*'}, mimetype='application/json')

    def test_request_with_url_without_prefix_on_prefixed_server(self):
        server = Server(default_handler, url_path_prefix="/api/v3.1/")
        with self.assertRaises(ItemNotFoundError):
            server(self.plain_environ, self.fake_start_response)

    def test_request_with_additional_headers(self):
        server = Server(default_handler, url_path_prefix="", additional_headers="X-Range: 20; X-Limit: 30")
        server(self.plain_environ, self.fake_start_response)
        target_response = json.dumps(default_handler("GET", "/books/20", {}, {}))
        self.assertTrue(self.response_adapter_mock.called)
        self.response_adapter_mock.assert_called_with(target_response, status=200,
                                                      headers={'Access-Control-Allow-Origin': '*',
                                                               "X-Range": "20", "X-Limit": "30"},
                                                      mimetype='application/json')

    def test_request_with_json_body(self):
        server = Server(default_handler)
        server(self.environ_with_data, self.fake_start_response)
        target_response = json.dumps(default_handler("POST", "/books/20", {}, self.data))
        self.assertTrue(self.response_adapter_mock.called)
        self.response_adapter_mock.assert_called_with(target_response, status=200,
                                                      headers={'Access-Control-Allow-Origin': '*'},
                                                      mimetype='application/json')

    def test_reqest_with_invalid_json_body(self):
        server = Server(default_handler, url_path_prefix="")
        server(self.environ_with_xml_data, self.fake_start_response)
        self.assertTrue(self.response_adapter_mock.called)
        # self.response_adapter_mock.assert_called_with(target_response, status=500,
        #                                               headers={'Access-Control-Allow-Origin': '*'},
        #                                               mimetype='application/json')

    @patch("time.sleep")
    def test_sleep_before_request(self, mocked_sleep: MagicMock):
        server = Server(default_handler, url_path_prefix="", sleep_before_request=200)
        server(self.plain_environ, self.fake_start_response)
        mocked_sleep.assert_called_with(0.2)

    def test_options_request(self):
        server = Server(default_handler)
        server(self.options_environ, self.fake_start_response)
        self.assertTrue(self.response_adapter_mock.called)
        self.response_adapter_mock.assert_called_with("", status=200, headers={
                                                      "Access-Control-Allow-Methods":
                                                      "GET, POST, PUT, PATCH, DELETE, OPTIONS",
                                                      "Access-Control-Allow-Origin": "*"})

    def tearDown(self) -> None:
        self.response_adapter_mock.stop()
        super().tearDown()


class TestErrorHandling(TestCase):
    def setUp(self) -> None:
        response_adapter = patch("data_server.core.server.Response")
        self.response_adapter_mock = response_adapter.start()
        self.response_adapter_mocked_instance = self.response_adapter_mock.return_value
        self.plain_environ = create_environ(path="/books/20", method="GET")
        self.plain_environ_with_url_prefix = create_environ(path="/api/v3.1/books/20", method="GET")
        self.options_environ = create_environ(path="/books/20", method="OPTIONS")
        self.fake_start_response = lambda status, header: {"status": status, "header": header}
        self.data = {"name": "A Book"}
        input_bytes = json.dumps(self.data).encode()
        self.environ_with_data = create_environ(path="/books/20", method="POST", mimetype="application/json",
                                                content_length=len(input_bytes),
                                                input_stream=BytesIO(input_bytes))
        super().setUp()

    def test_data_server_errors_handling(self):
        def handler(method, url, args, data): raise ItemNotFoundError("Not Found")
        server = Server(handler)
        server(self.plain_environ_with_url_prefix, self.fake_start_response)
        target_response = json.dumps({"error": {"description": "Not Found", "code": 404, "details": "Not Found, 404"}})
        self.assertTrue(self.response_adapter_mock.called)
        self.response_adapter_mock.assert_called_with(target_response, status=404, headers={
                                                      'Access-Control-Allow-Origin': '*'}, mimetype='application/json')

    def test_inbuilt_errors_handling(self):
        def handler(method, url, args, data): raise Exception("Not Found")
        server = Server(handler)
        server(self.plain_environ_with_url_prefix, self.fake_start_response)
        target_response = json.dumps({"error": {"description": "Not Found", "code": 500, "details": None}})
        self.assertTrue(self.response_adapter_mock.called)
        self.response_adapter_mock.assert_called_with(target_response, status=500, headers={
                                                      'Access-Control-Allow-Origin': '*'}, mimetype='application/json')
