import unittest
import unittest.mock as mock
from io import StringIO

from data_server.core.adapters.csv_adapter import CsvAdapter
from data_server.errors import CsvAdapterError


class TestCSVAdapter(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @mock.patch("os.path.exists", return_value=False)
    def test_initialization_with_file_that_does_not_exist(self, os_patch: mock.MagicMock) -> None:
        with self.assertRaises(CsvAdapterError):
            CsvAdapter("csv_file.csv")
        self.assertTrue(os_patch.called)

    @mock.patch("warnings.warn")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("builtins.open", return_value=StringIO("id,name\n1,pius"))
    def test_warning_when_not_csv_file_extension(self, open_mock: mock.MagicMock, os_patch: mock.MagicMock,
                                                 warn_patch: mock.MagicMock) -> None:
        CsvAdapter("csv_file.cvv")
        self.assertTrue(open_mock.called)
        self.assertTrue(os_patch.called)
        self.assertTrue(warn_patch.called)

    @mock.patch("os.path.exists", return_value=True)
    def test_initialization_with_file_that_exists(self, os_patch: mock.MagicMock) -> None:
        with mock.patch.object(CsvAdapter, 'read_data', return_value={}) as read_data_mock:
            adapter = CsvAdapter("csv_file.csv")
        self.assertTrue(os_patch.called_with("csv_file.csv"))
        self.assertDictEqual(adapter.get_data(), {})
        self.assertTrue(read_data_mock.called)

    def test_generate_key_with_none_key(self) -> None:
        key = CsvAdapter._generate_key("csv_file.csv")
        self.assertEqual(key, 'csv_file')
        key = CsvAdapter._generate_key("/usr/bin/csv_file.csv")
        self.assertEqual(key, 'csv_file')
        key = CsvAdapter._generate_key("C:\\user\\csv_file.csv")
        self.assertEqual(key, 'csv_file')
        key = CsvAdapter._generate_key("./file/csv_file.csv")
        self.assertEqual(key, 'csv_file')
        key = CsvAdapter._generate_key(".\\csv_file.csv")
        self.assertEqual(key, 'csv_file')

    def test_generate_key_with_not_none_key(self) -> None:
        key = CsvAdapter._generate_key("csv_file.csv", key="test_key")
        self.assertEqual(key, 'test_key')

    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("builtins.open", return_value=StringIO("id,name\n1,pius"))
    def test_read_data_with_valid_csv_file(self, open_patch: mock.MagicMock, os_patch: mock.MagicMock) -> None:
        adapter = CsvAdapter("csv_file.csv")
        self.assertTrue(os_patch.called_with("csv_file.csv"))
        self.assertTrue(open_patch.called_with("csv_file.csv"))
        self.assertDictEqual(adapter.get_data(), {'csv_file': [{'id': '1', 'name': 'pius'}]})

    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("builtins.open", return_value=StringIO(""))
    def test_save_data(self, open_patch: mock.MagicMock,
                       os_patch: mock.MagicMock, ) -> None:
        with mock.patch.object(CsvAdapter, 'read_data', return_value={'csv_file': [{'id': '1', 'name': 'pius'}]}):
            adapter = CsvAdapter("csv_file.csv")
            adapter.save_data()
        self.assertTrue(os_patch.called_with("csv_file.csv"))
        self.assertTrue(open_patch.called_with("csv_file.csv"))
