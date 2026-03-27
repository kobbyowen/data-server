class DataServerError(Exception):
    def __init__(self, description: str, code: int = 500):
        super().__init__(description, code)
        self.code = code
        self.description = description


class DataControllerError(DataServerError):
    def __init__(self, description: str, code: int = 400):
        super().__init__(description, code)


class ItemNotFoundError(DataControllerError):
    def __init__(self, description: str, code: int = 404):
        super().__init__(description, code)


class DuplicateIDFoundError(DataControllerError):
    pass


class AdapterError(DataServerError):
    def __init__(self, description: str, code: int = 400):
        super().__init__(description, code)


class CsvAdapterError(AdapterError):
    pass


class JSONAdapterError(AdapterError):
    pass
