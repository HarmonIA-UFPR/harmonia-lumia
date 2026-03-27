class UserAlreadyExistsException(Exception):
    def __init__(self, message: str = 'Usuário já cadastrado'):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(Exception):
    def __init__(self, message: str = 'Usuário não encontrado'):
        self.message = message
        super().__init__(self.message)
