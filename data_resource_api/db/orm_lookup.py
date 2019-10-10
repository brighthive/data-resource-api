from data_resource_api.db import Base


def create_orm(table_name, table_fields):
    table_stuff = {
        '__tablename__': table_name,
        '__table_args__': {'extend_existing': True},
        **table_fields
    }
    table = type(table_name, (Base,), table_stuff)
    return table


def print_all_orm():
    """Return class reference mapped to table.

    :param table_fullname: String with fullname of table.
    :return: Class reference or None.
    """
    for c in Base.__subclasses__():
        print(c.__tablename__)


def does_tablename_orm_exist(table_fullname):
    """Return class reference mapped to table.

    :param table_fullname: String with fullname of table.
    :return: Class reference or None.
    """
    for c in Base.__subclasses__():
        if hasattr(c, '__tablename__') and c.__tablename__ == table_fullname:
            return True
    return False


def get_orm_by_tablename(table_fullname):
    """Return class reference mapped to table.

    :param table_fullname: String with fullname of table.
    :return: Class reference or None.
    """
    for c in Base.__subclasses__():
        if hasattr(c, '__tablename__') and c.__tablename__ == table_fullname:
            return c


def find_duplicates_in_orm():
    """Return class reference mapped to table.

    :return: List of duplicate tables found
    """
    found = {}
    duplicates = {}

    for c in Base.__subclasses__():
        table = c.__tablename__
        if table in found:
            duplicates[table] = None
        
        found[table] = None

    return list(duplicates.keys())


def duplicates_in_orm():
    duplicate_list = find_duplicates_in_orm()
    return len(duplicate_list) != 0
            
