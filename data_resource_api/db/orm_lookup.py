from data_resource_api.db import Base

def get_class_by_tablename(table_fullname):
    """Return class reference mapped to table.

    :param table_fullname: String with fullname of table.
    :return: Class reference or None.
    """
    for c in Base.__subclasses__():
        print(c)
        print(c.__tablename__)
        if hasattr(c, '__tablename__') and c.__tablename__ == table_fullname:
            print(f'Returning {c} in orm lookup')
            return c

            