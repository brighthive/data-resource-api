"""ORM Factory.

A factory for building SQLAlchemy ORM models from a Frictionless TableSchema specification.

"""

import warnings
from tableschema import Schema
from sqlalchemy import Column, ForeignKey, MetaData, String, exc
from data_resource_api.db import Base
from data_resource_api.factories import TABLESCHEMA_TO_SQLALCHEMY_TYPES


class ORMFactory(object):
    """ORM Factory

    Note:
        This sole purpose of this factory is to build ORM models on demand for other
        factories and modules.

    """

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
                        type(table, (Base,), {
                            '__tablename__': table,
                            '__table_args__': {'extend_existing': True},
                            'id': Column(self.get_sqlalchemy_type(field_type), primary_key=True)
                        })
                except Exception as e:
                    return False, None
                return True, foreign_key_reference
        return False, None

    def create_sqlalchemy_fields(self, descriptor_fields: list, primary_key: str, foreign_keys=[]):
        """Build SQLAlchemy fields to be added to new table object.

        Args:
            descriptor_fields (list of dict):
            primary_key (str): The primary key field.
            foreign_keys (list): Collection of foreign key fields.

        Return:
            dict: SQLAlchemy fields to append to the new database object.

        """

        def is_required(descriptor_field):
            has_required_key_and_true = ('required' in descriptor_field.keys() and descriptor_field['required']) 
            has_required_in_constraints = (
                'constraints' in descriptor_field.keys() 
                and 'required' in descriptor_field['constraints'].keys() 
                and descriptor_field['constraints']['required']
            )
            return has_required_key_and_true or has_required_in_constraints

        sqlalchemy_fields = {}

        if isinstance(primary_key, str):
            primary_key = [primary_key]

        for descriptor_field in descriptor_fields:
            if is_required(descriptor_field):
                nullable = False
            else:
                nullable = True
            
            # If this is the primary key
            if descriptor_field['name'] in primary_key:
                sqlalchemy_fields[descriptor_field['name']] = Column(
                    self.get_sqlalchemy_type(descriptor_field['type']),
                    primary_key=True
                )
                continue

            # Otherwise check if its a foreign key
            is_foreign_key, reference_table = self.evaluate_foreign_key(
                foreign_keys,
                descriptor_field['name'],
                descriptor_field['type']
            )
            if is_foreign_key: 
                try:
                    sqlalchemy_fields[descriptor_field['name']] = Column(
                        self.get_sqlalchemy_type(descriptor_field['type']),
                        ForeignKey(
                            reference_table,
                            onupdate='CASCADE',
                            ondelete='CASCADE'
                        )
                    )
                except Exception as e:
                    print(f'An exception occured {e}')
                
                continue
            
            # It's a regular descriptor_field
            sqlalchemy_fields[descriptor_field['name']] = Column(
                self.get_sqlalchemy_type(descriptor_field['type']),
                nullable=nullable
            )

        return sqlalchemy_fields

    def get_sqlalchemy_type(self, data_type: str):
        """Convert Tableschema to SQLAlchemy type.

        Args:
            data_type (str): Tableschema type to look up in the table.

        Return:
            object: SQLAlchemy type based on Tableschema mapping.
        """
        try:
            return TABLESCHEMA_TO_SQLALCHEMY_TYPES[data_type]
        except Exception:
            return String

    def create_orm_from_dict(self, table_schema: dict, model_name: str, api_schema: dict):
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
                    custom_table_name = '{}_{}'.format(
                        custom_table[1], custom_table[2])
                    join_tables.append(custom_table_name)
            fields = self.create_sqlalchemy_fields(
                table_schema['fields'], table_schema['primaryKey'], foreign_keys)
            fields.update({
                '__tablename__': model_name,
                '__table_args__': {'extend_existing': True}
            })
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', category=exc.SAWarning)
                    orm_class = type(model_name, (Base,), fields)
            except Exception as e:
                orm_class = None
        return orm_class
