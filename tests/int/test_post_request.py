import json
import time
import typing as t

from tests.int import IntegrationTestCase
from tests.int.utils import Order, TestClient, TestServer, generate_order


class PostRequestTestCase(IntegrationTestCase):
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


class TestPostRequest(PostRequestTestCase):
    def test_post_request_adds_item_and_saves(self) -> None:
        new_order = {'orderNumber': 'POST-NEW-001', 'amount': 123.45}
        response = self.client.post('/api/v3/orders', data=new_order)
        self.assertEqual(response['status'], 201)
        self.assertIn('orderNumber', response['json'])
        self.assertEqual(response['json']['orderNumber'], 'POST-NEW-001')
        self.assertEqual(response['json']['amount'], 123.45)

        # Check file was updated
        with open(self.server.server_file) as f:
            data = json.load(f)
        created = next((b for b in data['orders'] if b.get('orderNumber') == 'POST-NEW-001'), None)
        self.assertIsNotNone(created)
        self.assertEqual(created['amount'], 123.45)

    # def test_post_request_with_existing_id_returns_error(self) -> None:
    #     self.reload_server(self.server.server_file, port=None, auto_generate_id=False)

    #     existing_order = self.orders[0]
    #     new_order = {
    #         self.server.id_name: existing_order[self.server.id_name],
    #         'orderNumber': 'POST-DUPLICATE-ID',
    #         'amount': 555.55,
    #     }
    #     response = self.client.post('/api/v3/orders', data=new_order)
    #     self.assertEqual(response['status'], 409)
    #     self.assertIn('error', response['json'])

    def test_post_request_missing_required_fields(self) -> None:
        new_order = {
            # Missing orderNumber and amount
        }
        response = self.client.post('/api/v3/orders', data=new_order)
        self.assertEqual(response['status'], 201)
