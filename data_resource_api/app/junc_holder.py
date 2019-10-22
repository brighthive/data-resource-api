class JuncHolder:
    static_lookup = {}

    @staticmethod
    def add_table(table_name, table):
        underscore_count = len(table_name.split('_')) - 1
        if underscore_count != 1:
            raise ValueError(f"There should be only one underscore but found {underscore_count}")
        
        if JuncHolder.find_collision(table_name):
            raise RuntimeError

        JuncHolder.static_lookup[table_name] = table

    @staticmethod
    def lookup_table(table_one, table_two):
        table_name_one = f'{table_one}_{table_two}'
        table = None

        try:
            table = JuncHolder.static_lookup[table_name_one]
        except KeyError:
            pass

        if table: return table

        table_name_two = f'{table_two}_{table_one}'

        try:
            table = JuncHolder.static_lookup[table_name_two]
        except KeyError:
            return None
        
        return table

    @staticmethod
    def reset():
        static_lookup = {}
