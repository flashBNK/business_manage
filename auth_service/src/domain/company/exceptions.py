class CompanyNotFound(Exception):
    def __init__(self):
        super().__init__("Company not found.")


class CompanyNameIsUsed(Exception):
    def __init__(self):
        super().__init__("Company name already used.")
