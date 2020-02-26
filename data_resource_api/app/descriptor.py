class Descriptor():
    """
    This is a utility class to encapsulate functions and operations
    related to descriptor files.
    """
    def __init__(self, descriptor: dict):
        self.table_name = descriptor['datastore']['tablename']
        self.table_schema = descriptor['datastore']['schema']
        self.api_schema = descriptor['api']['methods'][0]
        self.data_resource_name = descriptor['api']['resource']
