from data_resource_api.app.junc_holder import JuncHolder
from expects import expect, be_an, raise_error, have_property, equal, be_empty, be
import pytest


class TestTable:
    def __init__(self, table_name):
        self.__tablename__ = table_name


class TestJuncHolder(object):
    def test_use(self):
        JuncHolder.reset()

        test_table = []
        JuncHolder.add_table("parent/child", test_table)

        table_one = JuncHolder.lookup_table("parent", "child")
        table_two = JuncHolder.lookup_table("child", "parent")

        expect(table_one).to(be(test_table))
        expect(table_two).to(be(test_table))

    def test_error_two_underscore(self):
        JuncHolder.reset()

        with pytest.raises(ValueError):
            JuncHolder.add_table("parent/and/child", None)

    def test_error_no_underscore(self):
        JuncHolder.reset()

        with pytest.raises(ValueError):
            JuncHolder.add_table("parentchild", None)

    def test_use_full(self):
        JuncHolder.reset()

        test_table = []
        JuncHolder.add_table("parent/child", test_table)

        table_one = JuncHolder.lookup_full_table("parent/child")
        table_two = JuncHolder.lookup_full_table("child/parent")

        expect(table_one).to(be(test_table))
        expect(table_two).to(be(test_table))

    def test_full_error_two_underscore(self):
        with pytest.raises(ValueError):
            JuncHolder.lookup_full_table("parent/and/child")

    def test_full_error_no_underscore(self):
        with pytest.raises(ValueError):
            JuncHolder.lookup_full_table("parentchild")

    def test_allow_underscores(self):
        JuncHolder.reset()

        test_table = []
        JuncHolder.add_table("parent_table/child_table", test_table)

        table_one = JuncHolder.lookup_full_table("parent_table/child_table")
        table_two = JuncHolder.lookup_full_table("child_table/parent_table")

        expect(table_one).to(be(test_table))
        expect(table_two).to(be(test_table))