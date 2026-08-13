class SecretNotFound(Exception):
    def __init__(self):
        super().__init__(f'Account not found.')

class WrongSecretPassword(Exception):
    def __init__(self):
        super().__init__(f'Incorrect secret password.')