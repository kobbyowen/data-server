import unittest
from unittest.mock import patch, MagicMock
import typing as t
from copy import deepcopy
from data_server.errors import ItemNotFoundError, DuplicateIDFound
import data_server.data_server_types as dt
from data_server.core.data_controller import DataController
from tests.unit.fake_data import data_sample_with_empty_posts, data_sample_with_int_ids, data_sample_with_string_ids, \
    data_sample_with_id_name_as_uuid, data_sample_with_nested_items, data_sample


class TestInitialization(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_initialization(self) -> None:
        controller = DataController(data_sample_with_empty_posts)
        self.assertIsInstance(controller, DataController)

    def test_get_proper_id_type(self) -> None:
        controller = DataController(data_sample_with_int_ids)
        self.assertIs(controller.id_type, int)
        controller = DataController(data_sample_with_string_ids)
        self.assertIs(controller.id_type, str)


class TestGetItem(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_item_with_id(self) -> None:
        controller = DataController(data_sample_with_int_ids)
        item = controller.get_item(["posts"], 1)
        self.assertDictEqual(item, data_sample_with_int_ids["posts"][0])

        controller = DataController(
            data_sample_with_id_name_as_uuid, id_name="uuid")
        item = controller.get_item(["posts"], 1)
        self.assertDictEqual(
            item, data_sample_with_id_name_as_uuid["posts"][0])

    def test_get_item_with_id_with_nested_path(self) -> None:
        controller = DataController(data_sample_with_nested_items)
        item = controller.get_item(["posts", "comments", "all"], 1)
        self.assertDictEqual(item,
                             data_sample_with_nested_items["posts"]
                             ["comments"]["all"][0])

    def test_get_item_with_id_that_does_not_exist(self) -> None:
        controller = DataController(data_sample_with_int_ids)
        with self.assertRaises(ItemNotFoundError):
            controller.get_item(["posts"], 20)


class TestGetItems(unittest.TestCase):
    def test_get_items(self) -> None:
        controller = DataController(data_sample)
        items = controller.get_items(["books"])
        self.assertEqual(len(items), len(data_sample["books"]))
        # test if it is sorted by id which is default
        self.assertDictEqual(items[0], {
            "id": 1, "author": "Kobby Owen", "title": "Advanced Python"
        })

    def test_get_items_with_filters(self) -> None:
        items = DataController(data_sample).get_items(
            ["books"], author="Kobby Owen")
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertEqual(item["author"], "Kobby Owen")

        items = DataController(data_sample).get_items(
            ["books"], author="Kobby Owen", title="Everything about Python")
        self.assertEqual(len(items), 1)
        for item in items:
            self.assertEqual(item["author"], "Kobby Owen")
            self.assertEqual(item["title"], "Everything about Python")
        # verify sort order
        self.assertEqual(items[0]["id"], 15)

        items = DataController(data_sample).get_items(
            ["books"], author="Dummy Author", title="Everything about Python")
        self.assertEqual(len(items), 0)

    def test_get_items_in_sort_order(self) -> None:
        items = DataController(data_sample).get_items(
            ["books"], sort_by="author")
        self.assertEqual(len(items), len(data_sample["books"]))
        self.assertEqual(items[0]["author"], "Beverly Jones")
        self.assertEqual(items[len(items) - 1]["author"], "Pius Lins")

        items = DataController(data_sample).get_items(
            ["books"], sort_by="title", order="desc")
        self.assertEqual(len(items), len(data_sample["books"]))
        self.assertEqual(items[len(items) - 1]["title"], "Advanced Python")
        self.assertEqual(items[0]["title"], "Python In A Nutshell")

    def test_get_items_with_page_and_size(self) -> None:
        items = DataController(data_sample).get_items(
            ["books"], page=0, size=2)
        self.assertEqual(len(items), 2)
        items = DataController(data_sample).get_items(
            ["books"], page=3, size=2)
        self.assertEqual(len(items), 1)

    def test_get_items_with_path_that_does_not_exist(self) -> None:
        controller = DataController(data_sample_with_nested_items)
        with self.assertRaises(ItemNotFoundError):
            controller.get_item(["posts", "comments", "self"], 1)
        with self.assertRaises(ItemNotFoundError):
            controller.get_item(["posts", "comment", "all"], 1)


class TestDeleteItem(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = deepcopy(data_sample)

    def test_delete_item_with_correct_id(self) -> None:
        controller = DataController(self.data)
        controller.delete_item(["books"], 1)
        self.assertEqual(
            len(data_sample["books"]) - 1, len(self.data["books"]))
        self.assertEqual(
            len([item for item in self.data["books"] if item["id"] == 1]), 0)
        controller.delete_item(["books"], 2)
        self.assertEqual(
            len(data_sample["books"]) - 2, len(self.data["books"]))
        self.assertEqual(
            len([item for item in self.data["books"] if item["id"] == 2]), 0)

    def test_delete_item_with_correct_path_but_nonexisting_id(self) -> None:
        controller = DataController(self.data)
        with self.assertRaises(ItemNotFoundError):
            controller.delete_item(["books"], 3000)
        # make sure nothing is deleted
        self.assertEqual(len(data_sample), len(self.data))

    def test_delete_item_with_wrong_path(self) -> None:
        controller = DataController(self.data)
        with self.assertRaises(ItemNotFoundError):
            controller.delete_item(["path"], 1)
        # make sure nothing is deleted
        self.assertEqual(len(data_sample), len(self.data))


class TestAddItem(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.data = deepcopy(data_sample)

    def test_add_item_with_autogenerate_int_id(self) -> None:
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(
            self.data, autogenerate_id=True, id_name="id")
        results = controller.add_item(["books"], new_book)
        self.assertIs(controller.id_type, int)
        self.assertIn("id", results)
        self.assertIsInstance(results["id"], int)
        self.assertEqual(
            len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_autogenerate_string_id(self) -> None:
        self.data = deepcopy(data_sample_with_string_ids)
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(
            self.data, autogenerate_id=True, id_name="id")
        results = controller.add_item(["posts"], new_book)
        self.assertIs(controller.id_type, str)
        self.assertIn("id", results)
        self.assertIsInstance(results["id"], str)
        self.assertEqual(
            len([item for item in self.data["posts"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_timestamps(self) -> None:
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(
            self.data, autogenerate_id=True, id_name="id", use_timestamps=True)
        results = controller.add_item(["books"], new_book)
        self.assertIn("created_at", results)
        self.assertIn("updated_at", results)
        self.assertIsInstance(results["id"], int)
        self.assertEqual(
            len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_no_timestamps(self) -> None:
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(
            self.data, autogenerate_id=True, id_name="id",
            use_timestamps=False)
        results = controller.add_item(["books"], new_book)
        self.assertEqual(
            len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_existing_id(self) -> None:
        new_book = {"id": 1, "author": "Kobby Owen",
                    "title": "Testing With Python"}
        old_length = len(self.data)
        controller = DataController(
            self.data, autogenerate_id=False, id_name="id",
            use_timestamps=False)
        with self.assertRaises(DuplicateIDFound):
            controller.add_item(["books"], new_book)
        # make sure nothing is added
        self.assertEqual(old_length, len(self.data))

    def test_add_item_with_no_existing_id(self) -> None:
        new_book = {"id": 2000, "author": "Kobby Owen",
                    "title": "Testing With Python"}
        controller = DataController(
            self.data, autogenerate_id=False, id_name="id")
        results = controller.add_item(["books"], new_book)
        self.assertIs(controller.id_type, int)
        self.assertIn("id", results)
        self.assertIsInstance(results["id"], int)
        self.assertEqual(
            len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)


class TestPatchItem(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = deepcopy(data_sample)

    def test_patch_item_with_correct_id(self) -> None:
        new_data = {"author": "Pius Owen", "title": "Testing With Python"}
        controller = DataController(self.data)
        results = controller.patch_item(["books"], 1, new_data)
        items = controller.get_items(["books"], **new_data)
        self.assertEqual(len(items), 1)
        self.assertDictEqual(results, items[0])

    def test_patch_item_with_correct_path_but_nonexisting_id(self) -> None:
        new_data = {"author": "Pius Owen", "title": "Testing With Python"}
        controller = DataController(self.data)
        with self.assertRaises(ItemNotFoundError):
            controller.patch_item(["books"], 200, new_data)

    def test_patch_item_with_wrong_path(self) -> None:
        new_data = {"author": "Pius Owen", "title": "Testing With Python"}
        controller = DataController(self.data)
        with self.assertRaises(ItemNotFoundError):
            controller.patch_item(["all_books"], 1, new_data)

    def test_patch_item_with_data_containing_id(self) -> None:
        new_data = {"author": "Pius Owen",
                    "title": "Testing With Python", "test_id": 20}
        controller = DataController(self.data, id_name="test_id")
        with self.assertRaises(ValueError):
            controller.patch_item(["books"], 1, new_data)

    def test_patch_item_with_timestamps(self) -> None:
        new_data = {"author": "Pius Owen", "title": "Testing With Python"}
        controller = DataController(self.data, use_timestamps=True)
        results = controller.patch_item(["books"], 1, new_data)
        items = controller.get_items(["books"], **new_data)
        self.assertEqual(len(items), 1)
        self.assertIn("updated_at", results)


class TestReplaceItem(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.data = deepcopy(data_sample)

    def test_replace_item_with_correct_id(self) -> None:
        new_data = {"author": "Pius Owen", "title": "Testing With Python"}
        controller = DataController(self.data)
        results = controller.replace_item(["books"], 1, new_data)
        items = controller.get_items(["books"], **new_data)
        self.assertDictEqual(results, {**new_data, "id": 1})
        self.assertEqual(len(items), 1)

    def test_patch_item_with_data_containing_id(self) -> None:
        new_data = {"author": "Pius Owen",
                    "title": "Testing With Python", "test_id": 20}
        controller = DataController(self.data, id_name="test_id")
        with self.assertRaises(ValueError):
            controller.replace_item(["books"], 1, new_data)


class TestAutoGenerateId(unittest.TestCase):
    def setUp(self) -> None:
        sample_data_1 = {
            "books": [
                {
                    "id": 1,
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "created_at": "2023-04-09T22:18:20.421462",
                    "updated_at": "2023-04-09T22:18:20.421462"
                },
                {
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "created_at": "2023-04-09T22:18:20.421462",
                },
                {
                    "author": "Kobby Owen",
                    "title": "Python in a nutshell",
                    "updated_at": "2023-04-09T22:18:20.421462"
                }
            ]
        }
        sample_data_2 = {
            "books": [
                {
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "created_at": "2023-04-09T22:18:20.421462",
                    "updated_at": "2023-04-09T22:18:20.421462"
                },
                {
                    "book_id": "10",
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "updated_at": "2023-04-09T22:18:20.421462"
                },
                {
                    "author": "Kobby Owen",
                    "title": "Python in a nutshell",
                    "created_at": "2023-04-09T22:18:20.421462",
                }
            ]
        }

        self.data_sample_with_ints_ids = deepcopy(sample_data_1)
        self.data_sample_with_string_ids = deepcopy(sample_data_2)

        return super().setUp()

    def test_auto_generate_int_ids(self) -> None:
        controller = DataController(
            self.data_sample_with_ints_ids, autogenerate_id=True)
        generated_id = controller._autogenerate_id(
            t.cast(dt.JSONItems, self.data_sample_with_ints_ids["books"]))
        expected_ids = [2, 3]
        self.assertIn(generated_id, expected_ids)
        self.assertNotEqual(generated_id, 1)

    def test_autogenerate_id_with_single_data(self) -> None:
        controller = DataController(
            self.data_sample_with_ints_ids, autogenerate_id=True)
        generated_id = controller._autogenerate_id(
            t.cast(dt.JSONItems, [self.data_sample_with_ints_ids["books"][0]]))
        expected_ids = [2, 3]
        self.assertIn(generated_id, expected_ids)
        self.assertNotEqual(generated_id, 1)

    @patch("random.randint", side_effect=[1, 20])
    def test_auto_generate_int_ids_randomly(
            self, mocked_randint: MagicMock) -> None:
        controller = DataController(
            self.data_sample_with_ints_ids, autogenerate_id=True)
        generated_id = controller._autogenerate_id(
            t.cast(dt.JSONItems, self.data_sample_with_ints_ids["books"]),
            use_random=True)
        self.assertTrue(mocked_randint.called)
        self.assertEqual(generated_id, 20)

    @patch("data_server.core.data_controller.uuid4",
           side_effect=["10", "10", "20"],
           return_value="20")
    def test_auto_generate_string_ids(self, mocked_uuid: MagicMock) -> None:
        controller = DataController(
            self.data_sample_with_ints_ids, autogenerate_id=True,
            id_name="book_id")
        generated_id = controller._autogenerate_id(
            self.data_sample_with_string_ids["books"])
        self.assertTrue(mocked_uuid.called)
        self.assertIn(generated_id, "20")


class TestFixData(unittest.TestCase):
    def setUp(self) -> None:
        sample_data_1 = {
            "books": [
                {
                    "id": 5,
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "created_at": "2023-04-09T22:18:20.421462",
                    "updated_at": "2023-04-09T22:18:20.421462"
                },
                {
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "created_at": "2023-04-09T22:18:20.421462",
                },
                {
                    "author": "Kobby Owen",
                    "title": "Python in a nutshell",
                    "updated_at": "2023-04-09T22:18:20.421462"
                }
            ]
        }
        sample_data_2 = {
            "books": [
                {
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "created_at": "2023-04-09T22:18:20.421462",
                    "updated_at": "2023-04-09T22:18:20.421462"
                },
                {
                    "book_id": "10",
                    "author": "Pius Owen",
                    "title": "Testing with python",
                    "updated_at": "2023-04-09T22:18:20.421462"
                },
                {
                    "author": "Kobby Owen",
                    "title": "Python in a nutshell",
                    "created_at": "2023-04-09T22:18:20.421462",
                }
            ]
        }

        self.data_sample_with_ints_ids = t.cast(
            dt.JSONItem, deepcopy(sample_data_1))
        self.data_sample_with_string_ids = t.cast(dt.JSONItem,
                                                  deepcopy(sample_data_2))
        return super().setUp()

    def test_adding_automatic_integer_ids(self) -> None:
        DataController(
            self.data_sample_with_ints_ids, fix=True, use_timestamps=True)
        for book in self.data_sample_with_ints_ids["books"]:
            self.assertIn("id", book)
            self.assertIn("created_at", book)
            self.assertIn("updated_at", book)
            self.assertEqual(type(book["id"]), int)
        data = {"book": {
            "author": "Kobby Owen",
            "title": "Python in a nutshell",
            "created_at": "2023-04-09T22:18:20.421462",
        }}
        DataController(data, fix=True, use_timestamps=True)

    def test_adding_automatic_string_ids(self) -> None:
        DataController(
            self.data_sample_with_string_ids, fix=True, use_timestamps=True)
        for book in self.data_sample_with_string_ids["books"]:
            self.assertIn("id", book)
            self.assertIn("created_at", book)
            self.assertIn("updated_at", book)
            self.assertEqual(type(book["id"]), str)

    def test_removing_timestamps(self) -> None:
        DataController(
            self.data_sample_with_string_ids, fix=True, use_timestamps=False)
        for book in self.data_sample_with_string_ids["books"]:
            self.assertNotIn("created_at", book)
            self.assertNotIn("updated_at", book)


if __name__ == "__main__":
    unittest.main()
