from data_resource_api.app.data_model_manager import DataModelManagerSync
from expects import expect, be_an, raise_error, have_property, equal
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor,
    credentials_descriptor,
    programs_descriptor)

from sqlalchemy.ext.declarative import declarative_base


class TestDataModelManager():
    def test_load_descriptor_into_sql_alchemy_model(self):
        # init sql alchemy base
        Base = declarative_base()
        table_list = list(Base.metadata.tables.keys())
        expect(table_list).to(equal([]))

        # load descriptor and pass sql alchemy base
        DMM = DataModelManagerSync(Base)
        DMM.load_descriptor_into_sql_alchemy_model(frameworks_descriptor)
        table_list = list(Base.metadata.tables.keys())

        expect(table_list).to(equal(['frameworks/skills', 'frameworks']))

        # delete sqlalchemy base
        del Base
