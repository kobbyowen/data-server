import unittest
from typing import Dict, Text, Any
from data_server.core.adapters.adapter import DataAdapter
from tests.fake_data import data_sample


class TestAdapterInitialization(unittest.TestCase):
    def test_initialization_should_raise_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            DataAdapter("path/to/resource")

    def test_succesful_initialization(self) -> None:
        adapter = DataAdapter({})
        self.assertIsInstance(adapter, DataAdapter)


class TestSplitPath(unittest.TestCase):
    def test_split_path(self) -> None:
        paths = ["", "/path/to/resource", "path/to/resource", "path/to/resource", "/path/to/resource"]
        expected = [[], ["path", "to", "resource"], ["path", "to", "resource"], ["path", "to", "resource"]]

        for path, expected_result in zip(paths, expected):
            result = DataAdapter._split_paths(path)
            self.assertEqual(result, expected_result)


class TestDataAdapterMethods(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.adapter = DataAdapter(data_sample, autogenerate_id=True)

    def test_save_data(self) -> None:
        class TestAdapter(DataAdapter):
            def read_data(self) -> Dict[Text, Any]:
                return {}
        with self.assertRaises(NotImplementedError):
            TestAdapter("").save_data()

    def test_execute_get_item_request(self) -> None:
        item = self.adapter.execute_get_item_request("/books", 1)
        self.assertDictEqual(item, {"id": 1, "author": "Kobby Owen", "title": "Advanced Python"})

    def test_execute_get_request(self) -> None:
        items = self.adapter.execute_get_request("/books")
        self.assertEqual(len(items), len(data_sample["books"]))

    def test_execute_post_request(self) -> None:
        data = {"author": "Kobby Owen", "title": "Python In 30 Days"}
        item = self.adapter.execute_post_request("/books", data)
        self.assertDictContainsSubset(data, item)
        self.assertEqual(len(self.adapter.get_data()["books"]), len(data_sample["books"]) + 1)

    def test_execute_patch_request(self) -> None:
        data = {"title": "Python In 30 Days"}
        item = self.adapter.execute_patch_request("/books", 1, data)
        self.assertDictContainsSubset(data, item)

    def test_execute_put_request(self) -> None:
        data = {"author": "Kobby Owen", "title": "Python In 30 Days"}
        item = self.adapter.execute_put_request("/books", 1, data)
        self.assertDictContainsSubset(data, item)

    def test_execute_delete_request(self) -> None:
        self.adapter.execute_delete_request("/books", 1)
        self.assertEqual(len(self.adapter.get_data()["books"]), len(data_sample["books"]) - 1)

    def test_get_data(self) -> None:
        self.assertDictEqual(self.adapter.get_data(), data_sample)
