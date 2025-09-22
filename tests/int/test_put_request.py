import json
import time
import typing as t

from tests.int import IntegrationTestCase
from tests.int.utils import Order, TestClient, TestServer, generate_order


class PutRequestTestCase(IntegrationTestCase):
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
    def create_json_file(cls) -> str:
        cls.server = cls.server
        cls.orders = [
            generate_order(
                id_name=cls.server.id_name,
                id_type=str,
                created_at_key=cls.server.created_at_param_name,
                updated_at_key=cls.server.updated_at_param_name,
                add_timestamps=cls.server.use_timestamps,
            )
            for _ in [None] * 10
        ]
        cls.sorted_orders = cls.orders[:]
        cls.sorted_orders.sort(key=lambda order: order['key'])
        json_data = {'orders': cls.orders}
        server_file = f'tests/int/fixtures/{int(time.time() * 1000000)}.json'

        with open(server_file, 'w') as opened_server_file:
            json.dump(json_data, opened_server_file)
        return server_file


class TestPutRequest(PutRequestTestCase):
    def test_put_request_updates_item_and_saves(self) -> None:
        order = self.orders[0]
        order_id = order[self.server.id_name]
        new_data = {'orderNumber': 'PUT-UPDATED-001', 'amount': 999.99}
        response = self.client.put(f'/api/v3/orders/{order_id}', data=new_data)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['json'][self.server.id_name], order_id)
        self.assertEqual(response['json']['orderNumber'], 'PUT-UPDATED-001')
        self.assertEqual(response['json']['amount'], 999.99)

        # Check file was updated
        with open(self.server.server_file) as f:
            data = json.load(f)
        updated = next((b for b in data['orders'] if b[self.server.id_name] == order_id), None)
        self.assertIsNotNone(updated)
        self.assertEqual(updated['orderNumber'], 'PUT-UPDATED-001')
        self.assertEqual(updated['amount'], 999.99)

    def test_put_request_nonexistent_id_returns_error(self) -> None:
        non_existent_id = 'non-existent-id'
        new_data = {
            self.server.id_name: non_existent_id,
            'orderNumber': 'PUT-NOT-FOUND',
            'amount': 123.45,
        }
        response = self.client.put(f'/api/v3/orders/{non_existent_id}', data=new_data)
        self.assertEqual(response['status'], 404)
        self.assertIn('error', response['json'])

    def test_put_request_missing_id_in_body(self) -> None:
        order = self.orders[1]
        order_id = order[self.server.id_name]
        new_data = {'orderNumber': 'PUT-NO-ID', 'amount': 111.11}
        response = self.client.put(f'/api/v3/orders/{order_id}', data=new_data)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['json'][self.server.id_name], order_id)
        self.assertEqual(response['json']['orderNumber'], 'PUT-NO-ID')
        self.assertEqual(response['json']['amount'], 111.11)
