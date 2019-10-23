from data_resource_api.app.junc_holder import JuncHolder
from expects import expect, be_an, raise_error, have_property, equal, be_empty
import pytest

class TestTable:
    def __init__(self, table_name):
        self.__tablename__ = table_name

class TestJuncHolder(object):
    def test_use(self):
        test_table = TestTable("parent_child")
        JuncHolder.add_table("parent_child", test_table)

        table_one = JuncHolder.lookup_table("parent", "child")
        table_two = JuncHolder.lookup_table("child", "parent")

        expect(table_one.__tablename__).to(equal("parent_child"))
        expect(table_two.__tablename__).to(equal("parent_child"))

    def test_error_two_underscore(self):
        with pytest.raises(ValueError):
            JuncHolder.add_table("parent_and_child", None)

    def test_error_no_underscore(self):
        with pytest.raises(ValueError):
            JuncHolder.add_table("parentchild", None)

    