import unittest
from unittest.mock import patch
from main import create_server


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        argument_parser_patch = patch("main.ArgumentParser")
        server_patch = patch("main.Server")
        data_router_patch = patch("main.DataRouter")
        self.argument_parser_mock = argument_parser_patch.start()
        self.server_mock = server_patch.start()
        self.data_router_mock = data_router_patch.start()
        self.argument_parser_instance = self.argument_parser_mock.return_value
        self.argument_parser_instance.get_parsed_arguments.return_value = {
            "file": "", "id_name": "id", "sort_param_name": "sort",
            "order_param_name": "order", "page_param_name": "page",
            "size_param_name": "size", "auto_generate_ids": True,
            "use_timestamps": True, "created_at_key_name": "created_at",
            "updated_at_key_name": "updated_at", "page_size": 10,
            "url_path_prefix": "/", "host": "localhost", "port": 2020,
            "static_url_prefix": "static", "additional_headers": "",
            "sleep_before_request": 10, "disable_stdin": None}
        self.server_instance = self.server_mock.return_value
        self.server_instance.run.return_value = None
        self.data_router_instance = self.data_router_mock.return_value
        super().setUp()

    def tearDown(self) -> None:
        self.argument_parser_mock.stop()
        self.server_mock.stop()
        self.data_router_mock.stop()
        super().tearDown()

    def test_main(self) -> None:
        server = create_server()
        server.run()
        self.assertTrue(
            self.argument_parser_instance.get_parsed_arguments.called)
        self.assertTrue(
            self.server_instance.run.called)
