class CompanyReplicaNotFound(Exception):
    def __init__(self):
        super().__init__("Company_replica not found.")
