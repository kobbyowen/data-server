import os
from abc import ABC
from typing import Text, Any, Dict, List, Union
from csv import DictReader, DictWriter
from adapter import DataAdapter
from data_server.core.data_controller import JSONItem


class CsvAdapter(DataAdapter, ABC):
    """
    extends DataAdapter, handles conversion between CSV and Dictionary
    :args resource("path to a csv file or dictionary"), key("name of the csv file or key of dictionary")
    """

    def __init__(self, resource: Union[Text, JSONItem], key: Text = None, **kwargs: Any):
        if key is not None:
            self.key = key
        else:
            # pick the root element name before the extension.
            if isinstance(resource, str):
                assert resource.endswith('.csv'), "resource must be a valid csv file"
                self.key = self._split_paths(resource)[-1].split('.')[0]
            else:
                assert bool(resource), "Specified resource must be a non-empty dictionary."
                self.key = list(resource.keys())[0]

        super().__init__(resource, **kwargs)

    def read_data(self) -> Dict[Text, Any]:
        """
        reads csv file and returns dictionary
        :return: Dict[Text, Any]
        """
        try:
            assert self.resource.endswith('.csv')
            with open(self.resource, 'r') as f:
                dict_reader = DictReader(f)
                list_of_dicts = list(dict_reader)
                key_dict = dict({self.key: list_of_dicts})
                return key_dict
        except AssertionError as error:
            raise error
        except IOError as error:
            raise error

    def save_data(self) -> None:
        try:
            assert isinstance(self.read_data(), dict), "resource must be a non-empty dict"
            print("dict_key: {}".format(self.key))
            data_list = self.read_data().get(self.key)
            assert data_list is not None
            print(data_list)
            keys = data_list[0].keys()
            if not os.path.exists(self.resource):
                os.makedirs(self.resource)
            print("file_path: {}".format(self.resource))
            with open(self.resource, 'w', newline='') as output_file:
                dict_writer = DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(data_list)
            return
        except AssertionError as error:
            raise error


# test
sample_adapter = CsvAdapter("C:/Users/Dell Latitude 5300/Downloads/csv_adapter_sample.csv",
                            key="Owen is a full dataset")
print(sample_adapter.read_data())
print(sample_adapter.save_data())
