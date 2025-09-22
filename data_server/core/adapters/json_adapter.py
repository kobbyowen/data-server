from typing import Text, Any, Dict
import os
import json
from .adapter import DataAdapter
from data_server.errors import JSONAdapterError, AdapterError


class JSONAdapter(DataAdapter):
    def __init__(self, resource: Text, **kwargs: Any):
        if not os.path.exists(resource):
            raise AdapterError(f"{resource} does not exist")
        super().__init__(resource, **kwargs)

    def read_data(self) -> Dict[Text, Any]:
        json_contents = {}
        with open(self.resource) as json_file:
            try:
                json_contents = json.load(json_file)
            except json.decoder.JSONDecodeError as e:
                raise JSONAdapterError(f"Failed to decode json file : {e.args}")
        return json_contents

    def save_data(self) -> None:
        with open(self.resource, "w") as json_file:
            json.dump(self.get_data(), json_file, indent=4, sort_keys=True)
