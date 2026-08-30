class StructAdmNotFound(Exception):
    def __init__(self):
        super().__init__("StructAdm not found.")


class InvalidRequestStructAdm(Exception):
    def __init__(self):
        super().__init__("Invalid request input data.")


class NodeHasDependentsException(Exception):
    def __init__(self):
        super().__init__("Node has dependencies.")


class NodeHasRootStructAdm(Exception):
    def __init__(self):
        super().__init__("Node has root struct.")
