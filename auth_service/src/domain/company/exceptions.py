class CompanyNotFound(Exception):
    def __init__(self):
        super().__init__("Company not found.")
