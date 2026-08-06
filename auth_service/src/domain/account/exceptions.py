class EmailIsUsed(Exception):
    def __init__(self, email: str):
        super().__init__(f'User with email "{email}" already used.')

class AccountNotFound(Exception):
    def __init__(self):
        super().__init__(f'Account not found.')