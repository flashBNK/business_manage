class EmailIsUsed(Exception):
    def __init__(self, email: str):
        super().__init__(f'User with email "{email}" already used.')

class AccountNotFound(Exception):
    def __init__(self):
        super().__init__(f'Account not found.')

class EmailNotFound(Exception):
    def __init__(self):
        super().__init__(f'Email not found.')

class AccountAlreadyRegistered(Exception):
    def __init__(self):
        super().__init__("Registration for this account has already been completed.")

class AccountForbidden(Exception):
    def __init__(self):
        super().__init__("Account forbidden.")