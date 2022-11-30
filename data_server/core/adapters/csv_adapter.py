import os
import warnings
from typing import Text, Any, Dict, Optional, Union
from csv import DictReader, DictWriter
from .adapter import DataAdapter
from data_server.errors import CsvAdapterError


class CsvAdapter(DataAdapter):
    """
    extends DataAdapter, handles conversion between CSV and Dictionary
    :args resource("path to a csv file or dictionary"), key("name of the csv file or key of dictionary")
    """

    def __init__(self, resource: Union[Text], key: Optional[Text] = None, **kwargs: Any):
        self.key = self._generate_key(resource, key)
        if not os.path.exists(resource):
            raise CsvAdapterError(f"{resource} does not exist")
        super().__init__(resource, **kwargs)

    def read_data(self) -> Dict[Text, Any]:
        """
        reads csv file and returns dictionary
        :return: Dict[Text, Any]
        """

        if not self.resource.endswith('.csv'):
            warnings.warn("resource must be a valid CSV file")
        with open(self.resource, 'r') as f:
            dict_reader = DictReader(f)
            list_of_dicts = list(dict_reader)
            key_dict = dict({self.key: list_of_dicts})
            return key_dict

    def save_data(self) -> None:
        assert isinstance(self.read_data(), dict), "resource must be a non-empty dict"
        data_list = self.read_data().get(self.key)
        assert data_list is not None
        keys = data_list[0].keys()
        with open(self.resource, 'w', newline='') as output_file:
            dict_writer = DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data_list)

    @staticmethod
    def _generate_key(resource: Text, key: Optional[Text] = None) -> Text:
        if key is not None:
            return key
        else:
            # pick the root element name before the extension.
            return CsvAdapter._get_file_stem(resource)

    @staticmethod
    def _get_file_stem(resource: Text) -> Text:
        # detect separator used
        separator = "/" if "/" in resource else "\\"
        return resource.split(separator)[-1].split('.')[0]
