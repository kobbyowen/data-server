import unittest
from copy import deepcopy
from data_server.errors import ItemNotFoundError, DuplicateIDFound
from data_server.core.data_controller import DataController
from tests.fake_data import data_sample_with_empty_posts, data_sample_with_int_ids, data_sample_with_string_ids, \
    data_sample_with_id_name_as_uuid, data_sample_with_nested_items, data_sample


class TestInitialization(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_initialization(self):
        controller = DataController(data_sample_with_empty_posts)
        self.assertIsInstance(controller, DataController)

    def test_get_proper_id_type(self):
        controller = DataController(data_sample_with_int_ids)
        self.assertIs(controller.id_type, int)
        controller = DataController(data_sample_with_string_ids)
        self.assertIs(controller.id_type, str)


class TestGetItem(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_item_with_id(self):
        controller = DataController(data_sample_with_int_ids)
        item = controller.get_item(["posts"], 1)
        self.assertDictEqual(item, data_sample_with_int_ids["posts"][0])

        controller = DataController(data_sample_with_id_name_as_uuid, id_name="uuid")
        item = controller.get_item(["posts"], 1)
        self.assertDictEqual(item, data_sample_with_id_name_as_uuid["posts"][0])

    def test_get_item_with_id_with_nested_path(self):
        controller = DataController(data_sample_with_nested_items)
        item = controller.get_item(["posts", "comments", "all"], 1)
        self.assertDictEqual(item, data_sample_with_nested_items["posts"]["comments"]["all"][0])

    def test_get_item_with_id_that_does_not_exist(self):
        controller = DataController(data_sample_with_int_ids)
        with self.assertRaises(ItemNotFoundError):
            controller.get_item(["posts"], 20)


class TestGetItems(unittest.TestCase):
    def test_get_items(self):
        controller = DataController(data_sample)
        items = controller.get_items(["books"])
        self.assertEqual(len(items), len(data_sample["books"]))
        # test if it is sorted by id which is default
        self.assertDictEqual(items[0], {
            "id": 1, "author": "Kobby Owen", "title": "Advanced Python"
        })

    def test_get_items_with_filters(self):
        items = DataController(data_sample).get_items(["books"], author="Kobby Owen")
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertEqual(item["author"], "Kobby Owen")

        items = DataController(data_sample).get_items(["books"], author="Kobby Owen", title="Everything about Python")
        self.assertEqual(len(items), 1)
        for item in items:
            self.assertEqual(item["author"], "Kobby Owen")
            self.assertEqual(item["title"], "Everything about Python")
        # verify sort order
        self.assertEqual(items[0]["id"], 15)

        items = DataController(data_sample).get_items(["books"], author="Dummy Author", title="Everything about Python")
        self.assertEqual(len(items), 0)

    def test_get_items_in_sort_order(self):
        items = DataController(data_sample).get_items(["books"], sort_by="author")
        self.assertEqual(len(items), len(data_sample["books"]))
        self.assertEqual(items[0]["author"], "Beverly Jones")
        self.assertEqual(items[len(items) - 1]["author"], "Pius Lins")

        items = DataController(data_sample).get_items(["books"], sort_by="title", order="desc")
        self.assertEqual(len(items), len(data_sample["books"]))
        self.assertEqual(items[len(items) - 1]["title"], "Advanced Python")
        self.assertEqual(items[0]["title"], "Python In A Nutshell")

    def test_get_items_with_page_and_size(self):
        items = DataController(data_sample).get_items(["books"], page=0, size=2)
        self.assertEqual(len(items), 2)
        items = DataController(data_sample).get_items(["books"], page=3, size=2)
        self.assertEqual(len(items), 1)

    def test_get_items_with_path_that_does_not_exist(self):
        controller = DataController(data_sample_with_nested_items)
        with self.assertRaises(ItemNotFoundError):
            controller.get_item(["posts", "comments", "self"], 1)
        with self.assertRaises(ItemNotFoundError):
            controller.get_item(["posts", "comment", "all"], 1)


class TestDeleteItem(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.data = deepcopy(data_sample)

    def test_delete_item_with_correct_id(self):
        controller = DataController(self.data)
        controller.delete_item(["books"], 1)
        self.assertEqual(len(data_sample["books"]) - 1, len(self.data["books"]))
        self.assertEqual(len([item for item in self.data["books"] if item["id"] == 1]), 0)
        controller.delete_item(["books"], 2)
        self.assertEqual(len(data_sample["books"]) - 2, len(self.data["books"]))
        self.assertEqual(len([item for item in self.data["books"] if item["id"] == 2]), 0)

    def test_delete_item_with_correct_path_but_nonexisting_id(self):
        controller = DataController(self.data)
        with self.assertRaises(ItemNotFoundError):
            controller.delete_item(["books"], 3000)
        # make sure nothing is deleted
        self.assertEqual(len(data_sample), len(self.data))

    def test_delete_item_with_wrong_path(self):
        controller = DataController(self.data)
        with self.assertRaises(ItemNotFoundError):
            controller.delete_item(["path"], 1)
        # make sure nothing is deleted
        self.assertEqual(len(data_sample), len(self.data))


class TestAddItem(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.data = deepcopy(data_sample)

    def test_add_item_with_autogenerate_int_id(self):
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(self.data, autogenerate_id=True, id_name="id")
        results = controller.add_item(["books"], new_book)
        self.assertIs(controller.id_type, int)
        self.assertIn("id", results)
        self.assertIsInstance(results["id"], int)
        self.assertEqual(len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_autogenerate_string_id(self):
        self.data = deepcopy(data_sample_with_string_ids)
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(self.data, autogenerate_id=True, id_name="id")
        results = controller.add_item(["posts"], new_book)
        self.assertIs(controller.id_type, str)
        self.assertIn("id", results)
        self.assertIsInstance(results["id"], str)
        self.assertEqual(len([item for item in self.data["posts"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_timestamps(self):
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(self.data, autogenerate_id=True, id_name="id", use_timestamps=True)
        results = controller.add_item(["books"], new_book)
        self.assertIn("created_at", results)
        self.assertIn("updated_at", results)
        self.assertIsInstance(results["id"], int)
        self.assertEqual(len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_no_timestamps(self):
        new_book = {"author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(self.data, autogenerate_id=True, id_name="id", use_timestamps=False)
        results = controller.add_item(["books"], new_book)
        self.assertNotIn("created_at", results)
        self.assertNotIn("updated_at", results)
        self.assertEqual(len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)

    def test_add_item_with_existing_id(self):
        new_book = {"id": 1, "author": "Kobby Owen", "title": "Testing With Python"}
        old_length = len(self.data)
        controller = DataController(self.data, autogenerate_id=False, id_name="id", use_timestamps=False)
        with self.assertRaises(DuplicateIDFound):
            controller.add_item(["books"], new_book)
        # make sure nothing is added
        self.assertEqual(old_length, len(self.data))

    def test_add_item_with_no_existing_id(self):
        new_book = {"id": 2000, "author": "Kobby Owen", "title": "Testing With Python"}
        controller = DataController(self.data, autogenerate_id=False, id_name="id")
        results = controller.add_item(["books"], new_book)
        self.assertIs(controller.id_type, int)
        self.assertIn("id", results)
        self.assertIsInstance(results["id"], int)
        self.assertEqual(len([item for item in self.data["books"] if item["id"] == results["id"]]), 1)


class TestPatchItem(unittest.TestCase):
    def test_patch_item_with_correct_id(self):
        pass

    def test_patch_item_with_correct_path_but_nonexisting(self):
        pass

    def test_patch_item_with_wrong_path(self):
        pass

    def test_patch_item_with_teimstamps(self):
        pass


class TestReplaceItem(unittest.TestCase):
    def test_replace_item_with_correct_id(self):
        pass

    def test_replace_item_with_teimstamps(self):
        pass

    def test_replace_item_with_correct_path_but_nonexisting(self):
        pass

    def test_replace_item_with_wrong_path(self):
        pass


if __name__ == "__main__":
    unittest.main()
