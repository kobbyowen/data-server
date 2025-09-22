import unittest
import unittest.mock as mock
from io import StringIO

from data_server.core.adapters.json_adapter import JSONAdapter
from data_server.errors import AdapterError, JSONAdapterError


class TestJSONAdapter(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @mock.patch('os.path.exists', return_value=False)
    def test_initialization_with_file_that_does_not_exist(self, os_patch: mock.MagicMock) -> None:
        with self.assertRaises(AdapterError):
            JSONAdapter('json_file.json')
        self.assertTrue(os_patch.called)

    @mock.patch('os.path.exists', return_value=True)
    def test_initiaization_with_file_that_exists(self, os_patch: mock.MagicMock) -> None:
        with mock.patch.object(JSONAdapter, 'read_data', return_value={}) as read_data_mock:
            adapter = JSONAdapter('json_file.json')
        os_patch.assert_called_with('json_file.json')
        self.assertDictEqual(adapter.get_data(), {})
        self.assertTrue(read_data_mock.called)

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO('{}'))
    def test_read_data_with_valid_json_file(self, open_patch: mock.MagicMock, os_patch: mock.MagicMock) -> None:
        adapter = JSONAdapter('json_file.json')
        os_patch.assert_called_with('json_file.json')
        self.assertDictEqual(adapter.get_data(), {})

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO('-'))
    def test_read_data_with_invalid_json_file(self, open_patch: mock.MagicMock, os_patch: mock.MagicMock) -> None:
        with self.assertRaises(JSONAdapterError):
            JSONAdapter('json_file.json')
        self.assertTrue(open_patch.called)
        self.assertTrue(os_patch.called)

    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('builtins.open', return_value=StringIO('{}'))
    @mock.patch('json.dump', return_value=None)
    def test_save_data(self, json_patch: mock.MagicMock, open_patch: mock.MagicMock, os_patch: mock.MagicMock) -> None:
        with mock.patch.object(JSONAdapter, 'read_data', return_value={}):
            adapter = JSONAdapter('json_file.json')
            adapter.save_data()
        os_patch.assert_called_with('json_file.json')
        open_patch.assert_called_with('json_file.json', 'w')
        self.assertTrue(json_patch.called)
