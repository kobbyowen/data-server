import sys
from unittest import TestCase

from data_server.argument_parser import ArgumentParser


class TestArgumentParser(TestCase):
    def setUp(self) -> None:
        self.old_args = sys.argv
        return super().setUp()

    def tearDown(self) -> None:
        sys.argv = self.old_args
        return super().tearDown()

    def test_initialization(self) -> None:
        sys.argv = ['argument_parser.py', 'file']
        parser = ArgumentParser('test', 'Testing', 'Testing Epilog')
        self.assertTrue(parser)

    def test_get_controller_arguments(self) -> None:
        sys.argv = ['argument_parser.py', 'file', '--use-timestamps', 'True']
        parser = ArgumentParser('test', 'Testing', 'Testing Epilog')
        self.assertEqual(len(parser.get_parsed_controller_arguments()), 10)
        self.assertTrue(parser.get_parsed_controller_arguments()['use_timestamps'])

    def test_get_server_arguments(self) -> None:
        sys.argv = ['argument_parser.py', 'file', '--url-path-prefix', '/api/v3']
        parser = ArgumentParser(
            'test',
            'Testing',
            'Testing Epilog',
        )
        self.assertEqual(len(parser.get_parsed_server_arguments()), 8)
        self.assertEqual(parser.get_parsed_server_arguments()['url_path_prefix'], '/api/v3')

    def test_get_parsed_arguments(self) -> None:
        sys.argv = [
            'argument_parser.py',
            'file',
            '--url-path-prefix',
            '/api/v3',
            '--use-timestamps',
            'True',
        ]
        parser = ArgumentParser('test', 'Testing', 'Testing Epilog')
        self.assertEqual(len(parser.get_parsed_arguments()), 20)
        self.assertEqual(parser.get_parsed_arguments()['url_path_prefix'], '/api/v3')
        self.assertTrue(parser.get_parsed_arguments()['use_timestamps'])
