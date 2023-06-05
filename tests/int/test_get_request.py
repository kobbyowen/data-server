import json
import time
import typing as t
from pprint import pprint
from tests.int import IntegrationTestCase
from tests.int.utils import generate_order


class GetRequestTestCase(IntegrationTestCase):

    orders = []

    @classmethod
    def create_json_file(cls) -> t.Text:
        cls.orders = [
            generate_order(
                id_name=cls.server.id_name,
                created_at_key=cls.server.created_at_param_name,
                updated_at_key=cls.server.updated_at_param_name,
                add_timestamps=cls.server.use_timestamps)
            for _ in [None] * 30]
        cls.sorted_orders = cls.orders[:]
        cls.sorted_orders.sort(key=lambda order: order[cls.server.id_name])
        json_data = {"orders": cls.orders}
        server_file = f"tests/int/fixtures/{int(time.time() * 1000000)}.json"
        with open(server_file, "w") as opened_server_file:
            json.dump(json_data, opened_server_file)
        return server_file


class TestGetRequest(GetRequestTestCase):
    def test_get_all_orders_request(self) -> None:
        response = self.client.get("/api/v3/orders")
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.sorted_orders[:self.server.page_size])


class TestPaginatedGetRequest(GetRequestTestCase):

    def test_get_request_with_valid_page_and_size(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=0&{self.server.size_param_name}=10")
        self.assertEqual(response["status"], 200)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.sorted_orders[:10])

    def test_get_request_with_invalid_page(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=-1&{self.server.size_param_name}=10")
        self.assertEqual(response["status"], 400)
        self.assertIn("error", response["json"])
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=A&{self.server.size_param_name}=10")
        self.assertEqual(response["status"], 400)
        self.assertIn("error", response["json"])

    def test_get_request_with_invalid_size(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=0&{self.server.size_param_name}=-10")
        self.assertEqual(response["status"], 400)
        self.assertIn("error", response["json"])
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=0&{self.server.size_param_name}=A")
        self.assertEqual(response["status"], 400)
        self.assertIn("error", response["json"])

    def test_get_request_with_missing_size(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=0")
        self.assertEqual(response["status"], 200)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.sorted_orders[: self.server.page_size])

    def test_get_request_with_missing_page(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=0")
        self.assertEqual(response["status"], 200)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.sorted_orders[: self.server.page_size])

    def test_get_request_with_large_page_number(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.page_param_name}=100000")
        self.assertEqual(response["status"], 200)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            [])

    def test_get_request_with_large_size_number(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.size_param_name}=100000")
        self.assertEqual(response["status"], 200)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.sorted_orders)

    def test_pagination_navigation(self) -> None:

        for i in range(0, 10):
            response = self.client.get(
                f"/api/v3/orders?{self.server.page_param_name}={i}&{self.server.size_param_name}=2")
            self.assertEqual(response["status"], 200)
            self.assertEqual(
                response["json"],
                self.sorted_orders[i * 2: (i * 2) + 2])


class TestSortedGetRequest(GetRequestTestCase):
    def test_get_request_with_existing_sort_key(self) -> None:
        response = self.client.get(
            "/api/v3/orders")
        self.assertEqual(response["status"], 200)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.sorted_orders[:self.server.page_size])

    def test_get_request_with_a_different_sort_key(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.sort_param_name}=orderNumber")
        self.assertEqual(response["status"], 200)
        sorted_orders = self.orders[:]
        sorted_orders.sort(key=lambda order: order["orderNumber"])
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            sorted_orders[:self.server.page_size])

    def test_get_request_with_an_invalid_sort_key(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.sort_param_name}=noAttribute")
        pprint(response["json"])
        sorted_orders = self.orders[:]
        sorted_orders.sort(key=lambda order: order["createdAt"])
        self.assertEqual(response["status"], 200)
        # maintain same order
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            self.orders[:self.server.page_size])

    def test_get_request_with_sorting_in_ascending_order(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.sort_param_name}=orderNumber&{self.server.order_param_name}=asc")
        self.assertEqual(response["status"], 200)
        sorted_orders = self.orders[:]
        sorted_orders.sort(key=lambda order: order["orderNumber"])
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            sorted_orders[:self.server.page_size])

    def test_get_request_with_sorting_in_descending_order(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.sort_param_name}=orderNumber&{self.server.order_param_name}=desc")
        self.assertEqual(response["status"], 200)
        sorted_orders = self.orders[:]
        sorted_orders.sort(
            key=lambda order: order["orderNumber"],
            reverse=True)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            sorted_orders[:self.server.page_size])

    def test_get_request_with_invalid_sort_order(self) -> None:
        response = self.client.get(
            f"/api/v3/orders?{self.server.sort_param_name}=orderNumber&{self.server.order_param_name}=unknown")
        self.assertEqual(response["status"], 200)
        sorted_orders = self.orders[:]
        sorted_orders.sort(
            key=lambda order: order["orderNumber"],
            reverse=True)
        self.assertListEqual(
            t.cast(t.List[t.Any],
                   response["json"]),
            sorted_orders[:self.server.page_size])
