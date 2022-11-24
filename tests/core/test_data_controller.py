import unittest
from data_server.core.data_controller import DataController


class TestInitialization(unittest.TestCase):
    def test_initialization(self):
        controller = DataController({})
        self.assertIsInstance(controller, list)


if __name__ == "__main__":
    unittest.main()
