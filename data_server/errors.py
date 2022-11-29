class DataServerError(Exception):
    def __init__(self, code: int, description: str):
        super().__init__()
        self.code = code
        self.description = description


class DataControllerError(DataServerError):
    def __init__(self, description: str):
        super().__init__(400, description)


class ItemNotFoundError(DataControllerError):
    pass


class DuplicateIDFound(DataControllerError):
    pass


class AdapterError(DataServerError):
    def __init__(self, description: str):
        super().__init__(500, description)


class JSONAdapterError(AdapterError):
    pass
