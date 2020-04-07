import pytest
from data_resource_api.app.utils.junc_holder import JuncHolder
from expects import be, be_an, be_empty, equal, expect, have_property, raise_error


@pytest.mark.unit
def test_use():
    JuncHolder.reset()

    test_table = []
    JuncHolder.add_table("parent/child", test_table)

    table_one = JuncHolder.lookup_table("parent", "child")
    table_two = JuncHolder.lookup_table("child", "parent")

    expect(table_one).to(be(test_table))
    expect(table_two).to(be(test_table))


@pytest.mark.unit
def test_error_two_underscore():
    JuncHolder.reset()

    with pytest.raises(ValueError):
        JuncHolder.add_table("parent/and/child", None)


@pytest.mark.unit
def test_error_no_underscore():
    JuncHolder.reset()

    with pytest.raises(ValueError):
        JuncHolder.add_table("parentchild", None)


@pytest.mark.unit
def test_use_full():
    JuncHolder.reset()

    test_table = []
    JuncHolder.add_table("parent/child", test_table)

    table_one = JuncHolder.lookup_full_table("parent/child")
    table_two = JuncHolder.lookup_full_table("child/parent")

    expect(table_one).to(be(test_table))
    expect(table_two).to(be(test_table))


@pytest.mark.unit
def test_full_error_two_underscore():
    with pytest.raises(ValueError):
        JuncHolder.lookup_full_table("parent/and/child")


@pytest.mark.unit
def test_full_error_no_underscore():
    with pytest.raises(ValueError):
        JuncHolder.lookup_full_table("parentchild")


@pytest.mark.unit
def test_allow_underscores():
    JuncHolder.reset()

    test_table = []
    JuncHolder.add_table("parent_table/child_table", test_table)

    table_one = JuncHolder.lookup_full_table("parent_table/child_table")
    table_two = JuncHolder.lookup_full_table("child_table/parent_table")

    expect(table_one).to(be(test_table))
    expect(table_two).to(be(test_table))
