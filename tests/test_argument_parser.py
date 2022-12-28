from unittest import TestCase
from data_server.argument_parser import ArgumentParser


class TestArgumentParser(TestCase):
    def test_initialization(self) -> None:
        parser = ArgumentParser("test", "Testing", "Testing Epilog", [""])
        self.assertTrue(parser)

    def test_get_controller_arguments(self) -> None:
        parser = ArgumentParser("test", "Testing", "Testing Epilog", ["argument_parser.py", "--use-timestamps", "True"])
        self.assertEqual(len(parser.get_parsed_controller_arguments()), 10)
        self.assertTrue(parser.get_parsed_controller_arguments()["use_timestamps"])

    def test_get_server_arguments(self) -> None:
        parser = ArgumentParser("test", "Testing", "Testing Epilog", [
                                "argument_parser.py", "--url-path-prefix", "/api/v3"])
        self.assertEqual(len(parser.get_parsed_server_arguments()), 8)
        self.assertEqual(parser.get_parsed_server_arguments()["url_path_prefix"], "/api/v3")

    def test_get_parsed_arguments(self) -> None:
        parser = ArgumentParser("test", "Testing", "Testing Epilog", [
                                "argument_parser.py", "--url-path-prefix", "/api/v3", "--use-timestamps", "True"])
        self.assertEqual(len(parser.get_parsed_arguments()), 18)
        self.assertEqual(parser.get_parsed_arguments()["url_path_prefix"], "/api/v3")
        self.assertTrue(parser.get_parsed_arguments()["use_timestamps"])
