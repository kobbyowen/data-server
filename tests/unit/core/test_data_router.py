import typing as t
from unittest import TestCase
from unittest.mock import patch

from data_server.core.data_router import DataRouter
from data_server.errors import ItemNotFoundError


class TestDataRouterInitialization(TestCase):
    def setUp(self) -> None:
        adapter_patcher = patch('data_server.core.data_router.DataAdapter')
        csv_patcher = patch('data_server.core.data_router.CsvAdapter')
        json_adapter = patch('data_server.core.data_router.JSONAdapter')
        self.adapter_mock = adapter_patcher.start()
        self.csv_adapter_mock = csv_patcher.start()
        self.json_adapter_mock = json_adapter.start()
        super().setUp()

    def tearDown(self) -> None:
        self.adapter_mock.stop()
        self.csv_adapter_mock.stop()
        self.json_adapter_mock.stop()
        super().tearDown()

    def test_initialization_with_dictionary(self) -> None:
        router = DataRouter({})
        self.assertTrue(self.adapter_mock.called)
        self.assertEqual(router.resource_type, 'dict')

    def test_initialization_with_json_file(self) -> None:
        router = DataRouter('testfile.json')
        self.assertTrue(self.json_adapter_mock.called)
        self.assertEqual(router.resource_type, 'json')

    def test_initialization_with_csv_file(self) -> None:
        router = DataRouter('testfile.csv')
        self.assertTrue(self.csv_adapter_mock.called)
        self.assertEqual(router.resource_type, 'csv')

    def test_initialization_with_invalid_resource_type(self) -> None:
        router = DataRouter('unknown-file')
        self.assertEqual(router.resource_type, 'json')

    def test_get_url(self) -> None:
        router = DataRouter({})
        router.get_url_data()
        self.assertTrue(self.adapter_mock.called)


class TestDataRouterForGetRequests(TestCase):
    def setUp(self) -> None:
        self.item_response = {'name': 'Kobby'}
        self.items_response = [{'name': 'Kobby'}]
        json_adapter = patch('data_server.core.data_router.JSONAdapter')
        self.json_adapter_mock = json_adapter.start()
        self.json_adapter_mocked_instance = self.json_adapter_mock.return_value
        self.json_adapter_mocked_instance.get_urls.return_value = [
            '/posts',
            '/book',
            '/posts/today/noon',
        ]
        self.json_adapter_mocked_instance.get_url_data.return_value = [
            ('/posts', list),
            ('/book', dict),
            ('/posts/today/noon/', list),
        ]
        self.json_adapter_mocked_instance.execute_get_item_request.return_value = self.item_response
        self.json_adapter_mocked_instance.execute_get_request.return_value = self.items_response

        super().setUp()

    def test_get_request_with_index_url(self) -> None:
        router = DataRouter('testfile.json')
        result = router(method='get', url='/')
        self.assertEqual(
            result,
            [
                {'url': '/posts', 'methods': ['GET', 'POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE']},
                {'url': '/book', 'methods': ['GET']},
                {
                    'url': '/posts/today/noon/',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE'],
                },
            ],
        )

    def test_normal_get_request(self) -> None:
        router = DataRouter('testfile.json')
        result = router(method='get', url='/posts')
        self.assertListEqual(t.cast(t.Any, result), self.items_response)
        result = router(method='get', url='/posts/today/noon')
        self.assertListEqual(t.cast(t.Any, result), self.items_response)

    def test_get_request_with_url_with_id(self) -> None:
        router = DataRouter('testfile.json')
        result = router(method='get', url='/posts/1')
        self.assertDictEqual(t.cast(t.Any, result), self.item_response)
        result = router(method='get', url='/posts/today/noon/2')
        self.assertDictEqual(t.cast(t.Any, result), self.item_response)

    def test_get_with_url_not_found(self) -> None:
        router = DataRouter('testfile.json')
        with self.assertRaises(ItemNotFoundError):
            router(method='get', url='/false-url')

    def tearDown(self) -> None:
        self.json_adapter_mock.stop()
        super().tearDown()


class TestDataRouterPostRequest(TestCase):
    def setUp(self) -> None:
        self.item_response = {'name': 'Kobby'}
        json_adapter = patch('data_server.core.data_router.JSONAdapter')
        self.json_adapter_mock = json_adapter.start()
        self.json_adapter_mocked_instance = self.json_adapter_mock.return_value
        self.json_adapter_mocked_instance.get_urls.return_value = [
            '/posts',
            '/book',
            '/posts/today/noon',
        ]
        self.json_adapter_mocked_instance.get_url_data.return_value = [
            ('/posts', list),
            ('/book', dict),
            ('/posts/today/noon/', list),
        ]
        self.json_adapter_mocked_instance.execute_post_request.return_value = self.item_response

        super().setUp()

    def test_post_request(self) -> None:
        router = DataRouter('testfile.json')
        data = {'name': 'new-data'}
        result = router(method='post', url='/posts', data=data)
        self.assertDictEqual(t.cast(t.Any, result), self.item_response)
        self.json_adapter_mocked_instance.execute_post_request.assert_called_with('/posts', data)

    def tearDown(self) -> None:
        self.json_adapter_mock.stop()
        super().tearDown()


class TestDataRouterPatchAndPutRequest(TestCase):
    def setUp(self) -> None:
        self.item_response = {'name': 'Kobby'}
        json_adapter = patch('data_server.core.data_router.JSONAdapter')
        self.json_adapter_mock = json_adapter.start()
        self.json_adapter_mocked_instance = self.json_adapter_mock.return_value
        self.json_adapter_mocked_instance.get_urls.return_value = [
            '/posts',
            '/book',
            '/posts/today/noon',
        ]
        self.json_adapter_mocked_instance._controller.id_type = int
        self.json_adapter_mocked_instance.get_url_data.return_value = [
            ('/posts', list),
            ('/book', dict),
            ('/posts/today/noon/', list),
        ]
        self.json_adapter_mocked_instance.execute_put_request.return_value = self.item_response
        self.json_adapter_mocked_instance.execute_patch_request.return_value = self.item_response

        super().setUp()

    def test_put_request(self) -> None:
        router = DataRouter('testfile.json')
        data = {'name': 'new-data'}
        result = router(method='put', url='/posts/1', data=data)
        self.assertDictEqual(t.cast(t.Any, result), self.item_response)
        self.json_adapter_mocked_instance.execute_put_request.assert_called_with('/posts', 1, data)

    def test_patch_request(self) -> None:
        router = DataRouter('testfile.json')
        data = {'name': 'new-data'}
        result = router(method='patch', url='/posts/1', data=data)
        self.assertDictEqual(t.cast(t.Any, result), self.item_response)
        self.json_adapter_mocked_instance.execute_patch_request.assert_called_with('/posts', 1, data)

    def tearDown(self) -> None:
        self.json_adapter_mock.stop()
        super().tearDown()


class TestDataRouterDeleteRequest(TestCase):
    def setUp(self) -> None:
        json_adapter = patch('data_server.core.data_router.JSONAdapter')
        self.json_adapter_mock = json_adapter.start()
        self.json_adapter_mocked_instance = self.json_adapter_mock.return_value
        self.json_adapter_mocked_instance.get_urls.return_value = [
            '/posts',
            '/book',
            '/posts/today/noon',
        ]
        self.json_adapter_mocked_instance._controller.id_type = int
        self.json_adapter_mocked_instance.get_url_data.return_value = [
            ('/posts', list),
            ('/book', dict),
            ('/posts/today/noon/', list),
        ]
        self.json_adapter_mocked_instance.execute_delete_request.return_value = None

        super().setUp()

    def test_delete_request(self) -> None:
        router = DataRouter('testfile.json')
        data = {'name': 'new-data'}
        router(method='delete', url='/posts/1', data=data)
        self.json_adapter_mocked_instance.execute_delete_request.assert_called_with('/posts', 1)


class TestDataRouter(TestCase):
    def setUp(self) -> None:
        json_adapter = patch('data_server.core.data_router.JSONAdapter')
        self.json_adapter_mock = json_adapter.start()
        self.json_adapter_mocked_instance = self.json_adapter_mock.return_value
        self.json_adapter_mocked_instance.get_urls.return_value = [
            '/posts',
            '/book',
            '/posts/today/noon',
        ]
        self.json_adapter_mocked_instance._controller.id_type = int
        self.json_adapter_mocked_instance.get_url_data.return_value = [
            ('/posts', list),
            ('/book', dict),
            ('/posts/today/noon/', list),
        ]

        super().setUp()

    def test_delete_request(self) -> None:
        router = DataRouter('testfile.json')
        data = {'name': 'new-data'}
        with self.assertRaises(ValueError):
            router(method='unknown-method', url='/posts/1', data=data)
