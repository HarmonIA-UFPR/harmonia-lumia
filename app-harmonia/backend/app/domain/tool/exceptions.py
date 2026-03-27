class ToolNotFoundException(Exception):
    def __init__(self, message: str = 'Tool não encontrada'):
        self.message = message
        super().__init__(self.message)


class ToolAlreadyExistsException(Exception):
    def __init__(self, message: str = 'Tool já cadastrada'):
        self.message = message
        super().__init__(self.message)
