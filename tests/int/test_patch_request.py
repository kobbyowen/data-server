import json
import time
import typing as t
from tests.int import IntegrationTestCase
from tests.int.utils import generate_order, TestClient, TestServer, Order


class PatchRequestTestCase(IntegrationTestCase):

    orders: t.List[Order] = []
    sorted_orders: t.List[Order] = []

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    def setUp(self) -> None:
        self.client: TestClient = self._get_client()
        self.server: TestServer = self._get_server()
        return super().setUp()

    @classmethod
    def create_json_file(cls) -> t.Text:
        cls.server = cls.server
        cls.orders = [
            generate_order(
                id_name=cls.server.id_name,
                created_at_key=cls.server.created_at_param_name,
                updated_at_key=cls.server.updated_at_param_name,
                add_timestamps=cls.server.use_timestamps)
            for _ in [None] * 10]
        cls.sorted_orders = cls.orders[:]
        cls.sorted_orders.sort(key=lambda order: order["key"])
        json_data = {"orders": cls.orders}
        server_file = f"tests/int/fixtures/{int(time.time() * 1000000)}.json"
        with open(server_file, "w") as opened_server_file:
            json.dump(json_data, opened_server_file)
        return server_file


class TestPatchRequest(PatchRequestTestCase):
    def test_patch_request_updates_item_and_saves(self) -> None:
        order = self.orders[0]
        order_id = order[self.server.id_name]
        patch_data = {
            "amount": 888.88
        }
        response = self.client.patch(f"/api/v3/orders/{order_id}", data=patch_data)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["json"][self.server.id_name], order_id)
        self.assertEqual(response["json"]["amount"], 888.88)

        # Check file was updated
        with open(self.server.server_file) as f:
            data = json.load(f)
        updated = next((b for b in data["orders"] if b[self.server.id_name] == order_id), None)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["amount"], 888.88)

    def test_patch_request_nonexistent_id_returns_error(self) -> None:
        non_existent_id = 200000
        patch_data = {
            "amount": 555.55
        }
        response = self.client.patch(f"/api/v3/orders/{non_existent_id}", data=patch_data)
        self.assertEqual(response["status"], 404)
        self.assertIn("error", response["json"])

    def test_patch_request_missing_body(self) -> None:
        order = self.orders[1]
        order_id = order[self.server.id_name]
        response = self.client.patch(f"/api/v3/orders/{order_id}", data={})
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["json"][self.server.id_name], order_id)