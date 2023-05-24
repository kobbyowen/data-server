import unittest
import time
import os
import typing as t
from .utils import TestServer, TestClient


class IntegrationTestCase(unittest.TestCase):

    @classmethod
    def create_json_file(cls) -> t.Text:
        return "tests/int/fixtures/server-data.json"

    @classmethod
    def setUpClass(cls) -> None:
        port = 4580

        cls.server = TestServer(port)
        cls.server_file = cls.create_json_file()
        cls.server.server_file = cls.server_file
        cls.client = TestClient(port)
        cls.server.run()
        # give server time to initialize
        time.sleep(1)

    @classmethod
    def delete_json_file(cls) -> None:
        if cls.server_file:
            os.remove(cls.server_file)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.server:
            cls.server.stop()
        # give server time to cleanup
        time.sleep(1)
        cls.delete_json_file()
