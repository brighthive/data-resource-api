class JuncHolder:
    static_lookup = {}

    @staticmethod
    def add_table(table_name, table):
        divider_count = len(table_name.split('/')) - 1
        if divider_count != 1:
            raise ValueError(f"There should be only one slash but found {divider_count}")

        JuncHolder.static_lookup[table_name] = table

    @staticmethod
    def lookup_full_table(table_name):
        table_one, table_two = table_name.split('/')
        return JuncHolder.lookup_table(table_one, table_two)

    @staticmethod
    def lookup_table(table_one, table_two):
        table_name_one = f'{table_one}/{table_two}'
        table = None

        try:
            table = JuncHolder.static_lookup[table_name_one]
        except KeyError:
            pass

        if table is not None:
            return table

        table_name_two = f'{table_two}/{table_one}'

        try:
            table = JuncHolder.static_lookup[table_name_two]
        except KeyError:
            return None

        return table

    @staticmethod
    def reset():
        static_lookup = {}
