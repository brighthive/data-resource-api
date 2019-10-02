from data_resource_api.factories.orm_factory import ORMFactory
from data_resource_api.factories.data_resource_factory import DataResourceFactory
from tests.schemas import frameworks_descriptor, skills_descriptor

class FakeApi(object):
    def __init__(self):
        self.things = []

    def add_resource(self, new_api, resource, endpoint):
        new_thing = {
            "new_api": new_api,
            "resource": resource,
            "endpoint": endpoint}
        self.things.append(new_thing)

class TestStartup(object):
    def test_create_orm_from_dict(self):
        factory = ORMFactory()
        table_name = skills_descriptor['datastore']['tablename']
        table_schema = skills_descriptor['datastore']['schema']
        api_schema = skills_descriptor['api']['methods'][0]
        
        output = factory.create_orm_from_dict(table_schema, table_name, api_schema)
        print(type(output))
        print(output)


    def test_create_api_from_dict(self):
        factory = DataResourceFactory()
        table_name = skills_descriptor['datastore']['tablename']
        table_schema = skills_descriptor['datastore']['schema']
        api_schema = skills_descriptor['api']['methods'][0]
        fake_api = FakeApi()

        output = factory.create_api_from_dict(api_schema, table_name, table_name, fake_api, {}, table_schema, [])

        for thing in fake_api.things:
            print(thing)