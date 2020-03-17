"""ORM Factory.

A factory for building SQLAlchemy ORM models from a Frictionless TableSchema specification.

"""

import warnings
from tableschema import Schema
from sqlalchemy import Column, ForeignKey, String, exc, Table, Integer
from data_resource_api.factories import TABLESCHEMA_TO_SQLALCHEMY_TYPES
from data_resource_api.app.utils.junc_holder import JuncHolder
from data_resource_api.logging import LogFactory

logger = LogFactory.get_console_logger('orm-factory')


class ORMFactory(object):
    """ORM Factory

    Note:
        This sole purpose of this factory is to build ORM models on demand for other
        factories and modules.

    """

    def __init__(self, base):
        self.base = base

    def evaluate_foreign_key(self, foreign_keys, field_name, field_type):
        """Determine if a field is a foreign key.

        Args:
            foreign_keys (dict): A collection of foreign keys extracted from the
                Tableschame reference.
            field_name (str): Field to evaluate.
            field_type (str): Type of the field being evaluated.

        Note:
            This function will evaluate a field to determine if it is a foreign key.
            If the field is a foreign key, the function will determine if the table
            exists. If the table doesn't exist, the function will create the table
            with a primary key.

        Return:
            boolean, str: A flag indicating whether or not the field is a primary
                key and the name of the reference table.

        """

        for foreign_key in foreign_keys:
            if not isinstance(foreign_key['fields'], list):
                fk = [foreign_key['fields']]
            else:
                fk = foreign_key['fields']
            if field_name in fk:
                table = foreign_key['reference']['resource']
                field = foreign_key['reference']['fields']
                if not isinstance(field, list):
                    field = [field]
                foreign_key_reference = '{}.{}'.format(table, field[0])
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', category=exc.SAWarning)
                        type(table, (self.base,), {
                            '__tablename__': table,
                            '__table_args__': {'extend_existing': True},
                            'id': Column(self.get_sqlalchemy_type(field_type), primary_key=True)
                        })
                except Exception as e:
                    return False, None
                return True, foreign_key_reference
        return False, None

    def create_sqlalchemy_fields(
            self, fields: dict, primary_key, foreign_keys=[]):
        """Build SQLAlchemy fields to be added to new table object.

        Args:
            fields (dict):
            primary_key (str): The primary key field.
            foreign_keys (list): Collection of foreign key fields.

        Return:
            dict: SQLAlchemy fields to append to the new dataself.base object.

        """
        sqlalchemy_fields = {}
        if isinstance(primary_key, str):
            primary_key = [primary_key]
        for field in fields:
            if ('required' in field.keys() and field['required']) or \
                    ('constraints' in field.keys() and 'required' in field['constraints'].keys() and field['constraints']['required']):
                nullable = False
            else:
                nullable = True
            if field['name'] in primary_key:
                sqlalchemy_fields[field['name']] = Column(
                    self.get_sqlalchemy_type(field['type']), primary_key=True)
            else:
                is_foreign_key, reference_table = self.evaluate_foreign_key(
                    foreign_keys, field['name'], field['type'])
                if not is_foreign_key:
                    sqlalchemy_fields[field['name']] = Column(
                        self.get_sqlalchemy_type(field['type']), nullable=nullable)
                else:
                    try:
                        sqlalchemy_fields[field['name']] = Column(
                            self.get_sqlalchemy_type(
                                field['type']), ForeignKey(reference_table, onupdate='CASCADE', ondelete='CASCADE'))
                    except Exception as e:
                        logger.error(
                            "Error in create_sqlalchemy_fields", exc_info=True)
        return sqlalchemy_fields

    def get_sqlalchemy_type(self, data_type: str):
        """Convert Tableschema to SQLAlchemy type.

        Args:
            data_type (str): Tableschema type to look up in the table.

        Return:
            object: SQLAlchemy type self.based on Tableschema mapping.
        """
        try:
            return TABLESCHEMA_TO_SQLALCHEMY_TYPES[data_type]
        except Exception:
            return String

    def create_orm_from_dict(self, table_schema: dict,
                             model_name: str, api_schema: dict):
        """Create a SQLAlchemy model from a Frictionless Table Schema spec.

        Args:
            table_schema (dict): The Frictionless Table Schema as a dict.
            model_name (str): Name of the ORM model (i.e. table)
            api_schema (dict): The API schema to identify custom endpoints.

        Returns:
            object: The SQLAlchemy ORM class.

        """

        orm_class = None
        schema = Schema(table_schema)
        if schema.valid:
            if 'foreignKeys' in table_schema:
                foreign_keys = table_schema['foreignKeys']
            else:
                foreign_keys = []

            join_tables = []

            if 'custom' in api_schema:
                for custom_resource in api_schema['custom']:
                    custom_table = custom_resource['resource'].split('/')
                    custom_table_name = f'{custom_table[1]}/{custom_table[2]}'
                    join_tables.append(custom_table_name)

            logger.debug(f"found join tables: '{join_tables}'")

            fields = self.create_sqlalchemy_fields(
                table_schema['fields'], table_schema['primaryKey'], foreign_keys)

            fields.update({
                '__tablename__': model_name,
                '__table_args__': {'extend_existing': True}
            })

            for join_table in join_tables:
                self.process_join_table(join_table)

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', category=exc.SAWarning)
                    orm_class = type(model_name, (self.base,), fields)
            except Exception as e:
                logger.error("Error in create_orm_from_dict", exc_info=True)
                orm_class = None

        return orm_class

    def process_join_table(self, join_table: str):
        """Handles the creation of an association table.

        Args:
            join_table (str): String name of the association table
        """
        logger.info("processing " + join_table)
        tables = join_table.split('/')

        if JuncHolder.lookup_full_table(join_table) is not None:
            return

        try:
            association_table = Table(
                join_table,
                self.base.metadata,
                Column(
                    f'{tables[0]}_id',
                    Integer,
                    ForeignKey(f'{tables[0]}.id'),
                    primary_key=True),
                Column(
                    f'{tables[1]}_id',
                    Integer,
                    ForeignKey(f'{tables[1]}.id'),
                    primary_key=True),
                extend_existing=True
            )
        except Exception as e:
            logger.error(
                f"Error on create junc table '{join_table}'",
                exc_info=True)

        JuncHolder.add_table(join_table, association_table)
