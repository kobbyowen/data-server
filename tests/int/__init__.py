import unittest
import time
import os
import random
import typing as t
from .utils import TestServer, TestClient


class IntegrationTestCase(unittest.TestCase):

    server: t.Optional[TestServer] = None
    client: t.Optional[TestClient] = None

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.server_file: str = ""

    @classmethod
    def create_json_file(cls) -> t.Text:
        return "tests/int/fixtures/server-data.json"

    @classmethod
    def setUpClass(cls) -> None:
        port = random.randrange(10000, 60000)
        cls.server = TestServer(port)
        cls.port = port 
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
    def reload_server(
        cls,
        server_file: t.Optional[str] = None,
        port: t.Optional[int] = None,
        **server_options
    ) -> None:
        """Stops the current server and starts a new one with the given options."""
        if cls.server:
            cls.server.stop()
            time.sleep(1)
        if port is None:
            port = cls.port
        if server_file is None:
            server_file = cls.create_json_file()
        cls.server = TestServer(port, server_file=server_file, **server_options)
        cls.server_file = server_file
        cls.server.server_file = server_file
        cls.client = TestClient(port)
        cls.server.run()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.server:
            cls.server.stop()
        # give server time to cleanup
        time.sleep(1)
        cls.delete_json_file()

    @classmethod
    def _get_client(cls) -> TestClient:
        if cls.client:
            return cls.client
        raise ValueError("client is not configured")

    @classmethod
    def _get_server(cls) -> TestServer:
        if cls.server:
            return cls.server
        raise ValueError("server is not configured")
