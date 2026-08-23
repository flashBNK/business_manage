class SecretNotFound(Exception):
    def __init__(self):
        super().__init__("Account not found.")


class WrongSecretPassword(Exception):
    def __init__(self):
        super().__init__("Incorrect secret password.")
