class RegistrationSagaNotFound(Exception):
    def __init__(self) -> None:
        super().__init__("Registration SAGA not found.")
