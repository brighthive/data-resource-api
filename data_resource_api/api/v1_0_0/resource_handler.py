"""Generic Resource Handler.

"""

import math
import re
from collections import OrderedDict
from tableschema import Schema, validate
from brighthive_authlib import token_required
from data_resource_api.config import ConfigurationFactory
from data_resource_api.db import Session
from data_resource_api.app.utils.junc_holder import JuncHolder
from data_resource_api.logging import LogFactory
from data_resource_api.app.utils.exception_handler import ApiError, ApiUnhandledError, InternalServerError, NoRequestBodyFound
from sqlalchemy import and_
from data_resource_api.app.utils.exception_handler import SchemaValidationFailure


class ResourceHandler(object):
    def __init__(self):
        self.logger = LogFactory.get_console_logger('resource-handler')

    def build_json_from_object(self, obj: object, restricted_fields: dict = []):
        resp = {key: value if value is not None else '' for key, value in obj.__dict__.items(
        ) if not key.startswith('_') and not callable(key) and key not in restricted_fields}
        return resp

    def compute_offset(self, page: int, items_per_page: int) -> int:
        """Compute the offset value for pagination.
        Args:
            page (int): The current page to compute the offset from.
            items_per_page (int): Number of items per page.
        Returns:
            int: The offset value.
        """
        return int(int(int(page) - 1) * int(items_per_page))

    def compute_page(self, offset: int, items_per_page: int) -> int:
        """Compute the current page number based on offset.
        Args:
            offset (int): The offset to use to compute the page.
            items_per_page (int): Nimber of items per page.
        Returns:
            int: The page number.
        """

        return int(math.ceil(((int(offset) + 1) / int(items_per_page))))

    def build_links(self, endpoint: str, offset: int, limit: int, rows: int):
        """Build links for a paginated response
        Args:
            endpoint (str): Name of the endpoint to provide in the link.
            offset (int): Database query offset.
            limit (int): Number of items to return in query.
            rows (int): Count of rows in table.

        Returns:
            dict: The links based on the offset and limit
        """
        offset = int(offset)
        limit = int(limit)
        rows = int(rows)

        # URL and pages
        url_link = '/{}?offset={}&limit={}'
        total_pages = int(math.ceil(int(rows) / int(limit)))
        current_page = self.compute_page(offset, limit)

        # Links
        current = OrderedDict()
        first = OrderedDict()
        prev = OrderedDict()
        next = OrderedDict()
        last = OrderedDict()
        links = []

        current['rel'] = 'self'
        current['href'] = url_link.format(endpoint, offset, limit)
        links.append(current)

        first['rel'] = 'first'
        first['href'] = url_link.format(
            endpoint, self.compute_offset(1, limit), limit)
        links.append(first)

        if current_page > 1:
            prev['rel'] = 'prev'
            prev['href'] = url_link.format(
                endpoint, self.compute_offset(current_page - 1, limit), limit)
            links.append(prev)

        if current_page < total_pages:
            next['rel'] = 'next'
            next['href'] = url_link.format(
                endpoint, self.compute_offset(current_page + 1, limit), limit)
            links.append(next)

        last['rel'] = 'last'
        last['href'] = url_link.format(
            endpoint, self.compute_offset(total_pages, limit), limit)
        links.append(last)

        return links

    def validate_email(email_address):
        """Rudimentary email address validator.
        Args:
            email_address (str): Email address string to validate.
        Return:
            bool: True if the email address is valid, False if not.
        """
        email_regex = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
        is_valid = False

        try:
            if email_regex.match(email_address):
                is_valid = True
        except Exception:
            pass

        return is_valid

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def get_all_secure(self, data_model, data_resource_name,
                       restricted_fields, offset=0, limit=1):
        """Wrapper method for get_all method.

        Args:
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            offset (int): Pagination offset.
            limit (int): Result limit.

        Return:
            function: The wrapped method.

        """
        return self.get_all(data_model, data_resource_name,
                            restricted_fields, offset, limit)

    def get_all(self, data_model, data_resource_name,
                restricted_fields, offset=0, limit=1):
        """ Retrieve a paginated list of items.

        Args:
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            offset (int): Pagination offset.
            limit (int): Result limit.

        Return:
            dict, int: The response object and associated HTTP status code.
        """
        session = Session()
        response = OrderedDict()
        response[data_resource_name] = []
        response['links'] = []
        links = []

        try:
            results = session.query(data_model).limit(
                limit).offset(offset).all()
            for row in results:
                response[data_resource_name].append(
                    self.build_json_from_object(row, restricted_fields))
            row_count = session.query(data_model).count()
            if row_count > 0:
                links = self.build_links(
                    data_resource_name, offset, limit, row_count)
            response['links'] = links
        except Exception:
            raise InternalServerError()

        session.close()
        return response, 200

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def query_secure(self, data_model, data_resource_name,
                     restricted_fields, table_schema, request_obj):
        """Wrapper method for query."""
        return self.query(data_model, data_resource_name,
                          restricted_fields, table_schema, request_obj)

    def query(self, data_model, data_resource_name,
              restricted_fields, table_schema, request_obj):
        """Query the data resource."""

        try:
            request_obj = request_obj.json
        except Exception:
            raise NoRequestBodyFound()

        errors = []
        _ = Schema(table_schema)
        accepted_fields = []
        response = OrderedDict()
        response['results'] = []
        if validate(table_schema):
            for field in table_schema['fields']:
                if field['name'] not in restricted_fields:
                    accepted_fields.append(field['name'])
            for field in request_obj.keys():
                if field not in accepted_fields:
                    errors.append(
                        'Unknown or restricted field \'{}\' found.'.format(field))
            if len(errors) > 0:
                raise ApiUnhandledError('Invalid request body.', 400, errors)
            else:
                try:
                    session = Session()
                    results = session.query(
                        data_model).filter_by(**request_obj)
                    for row in results:
                        response['results'].append(
                            self.build_json_from_object(row, restricted_fields))

                    if len(response['results']) == 0:
                        return {'message': 'No matches found'}, 404
                    else:
                        return response, 200
                except Exception:
                    raise ApiUnhandledError(
                        'Failed to create new resource.', 400)
                finally:
                    session.close()
        else:
            raise SchemaValidationFailure()

        return {'message': 'querying data resource'}, 200

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def insert_one_secure(
            self, data_model, data_resource_name, table_schema, request_obj):
        """Wrapper method for insert one method.

        Args:
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.
            request_obj (dict): HTTP request object.

        Return:
            function: The wrapped method.

        """
        return self.insert_one(
            data_model, data_resource_name, table_schema, request_obj)

    def insert_one(self, data_model, data_resource_name,
                   table_schema, request_obj):
        """Insert a new object.

        Args:
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.
            request_obj (dict): HTTP request object.

        Return:
            dict, int: The response object and associated HTTP status code.
        """
        try:
            request_obj = request_obj.json
        except Exception:
            raise NoRequestBodyFound()

        _ = Schema(table_schema)
        errors = []
        accepted_fields = []

        if not validate(table_schema):
            raise SchemaValidationFailure()

        # Check for required fields
        for field in table_schema['fields']:
            accepted_fields.append(field['name'])

            if field['required'] and not field['name'] in request_obj.keys():
                errors.append(
                    f"Required field '{field['name']}' is missing."
                )

        valid_fields = []
        many_query = []

        for field in request_obj.keys():
            if field in accepted_fields:
                valid_fields.append(field)
            else:
                junc_table = JuncHolder.lookup_table(field, data_resource_name)

                if junc_table is not None:
                    values = request_obj[field]
                    if not isinstance(values, list):
                        values = [values]
                    many_query.append([field, values, junc_table])
                else:
                    errors.append(f"Unknown field '{field}' found.")

        if len(errors) > 0:
            raise ApiError('Invalid request body.', 400, errors)

        try:
            session = Session()
            new_object = data_model()
            for field in valid_fields:
                value = request_obj[field]
                setattr(new_object, field, value)
            session.add(new_object)
            session.commit()
            id_value = getattr(new_object, table_schema['primaryKey'])

            # process the many_query
            for field, values, table in many_query:
                self.process_many_query(
                    session, table, id_value, field, data_resource_name, values)

            return {'message': 'Successfully added new resource.',
                    'id': id_value}, 201
        except Exception:
            raise ApiUnhandledError('Failed to create new resource.', 400)
        finally:
            session.close()

    def process_many_query(self, session: object, table, id_value: int,
                           field: str, data_resource_name: str, values: list):
        """Iterates over values and adds the items to the junction table

        Args:
            session (object): sqlalchemy session object
            id_value (int): Newly created resource of type data_resource_name
            field (str): This is the field name
            data_resource_name (str): This is the resource type (table name) of the given resource
            values (list): Holds data to be inserted into the junction table
        """
        parent_column = f'{data_resource_name}_id'
        relationship_column = f'{field}_id'

        for value in values:
            try:
                cols = {
                    f'{parent_column}': id_value,
                    f'{relationship_column}': value
                }

                insert = table.insert().values(**cols)
                session.execute(insert)
                session.commit()

            except Exception as e:
                # psycopg2.errors.UniqueViolation
                if e.code == 'gkpj':
                    session.rollback()
                else:
                    raise InternalServerError()

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def get_one_secure(self, id, data_model, data_resource_name, table_schema):
        """Wrapper method for get one method.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            function: The wrapped method.

        """
        return self.get_one(id, data_model, data_resource_name, table_schema)

    def get_one(self, id, data_model, data_resource_name, table_schema):
        """Retrieve a single object from the data model based on it's primary key.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            dict, int: The response object and the HTTP status code.

        """
        try:
            primary_key = table_schema['primaryKey']
            session = Session()
            result = session.query(data_model).filter(
                getattr(data_model, primary_key) == id).first()
            response = self.build_json_from_object(result)
            return response, 200
        except Exception:
            raise ApiUnhandledError(f"Resource with id '{id}' not found.", 404)
        finally:
            session.close()

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def get_many_one_secure(self, id: int, parent: str, child: str):
        """Wrapper method for get many method.

        Args:
            id (int): Given ID of type parent
            parent (str): Type of parent
            child (str): Type of child

        Return:
            function: The wrapped method.

        """
        return self.get_many_one(
            id, parent, child)

    def get_many_one(self, id: int, parent: str, child: str):
        """Retrieve the many to many relationship data of a parent and child.

        Args:
            id (int): Given ID of type parent
            parent (str): Type of parent
            child (str): Type of child
        """
        join_table = JuncHolder.lookup_table(parent, child)

        # This should not be reachable
        # if join_table is None:
        # return {'error': f"relationship '{child}' of '{parent}' not found."}
        try:
            session = Session()
            parent_col_str = f'{parent}_id'
            child_col_str = f'{child}_id'

            cols = {parent_col_str: id}
            query = session.query(join_table).filter_by(**cols).all()

            children = []
            for row in query:
                # example - {'programs_id': 2, 'credentials_id': 3}
                row_dict = row._asdict()
                children.append(row_dict[child_col_str])

        except Exception:
            raise InternalServerError()

        finally:
            session.close()

        return {f'{child}': children}, 200

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def put_many_one_secure(self, id: int, parent: str, child: str, values):
        """Wrapper method for put many method.

        Args:
            id (int): Given ID of type parent
            parent (str): Type of parent
            child (str): Type of child

        Return:
            function: The wrapped method.

        """
        return self.put_many_one(self, id, parent, child, values)

    def put_many_one(self, id: int, parent: str, child: str, values):
        """put data for a many to many relationship of a parent and child.

        Args:
            id (int): Given ID of type parent
            parent (str): Type of parent
            child (str): Type of child
        """
        try:
            session = Session()
            junc_table = JuncHolder.lookup_table(parent, child)

            # delete all relations
            parent_col = getattr(junc_table.c, f'{parent}_id')
            del_st = junc_table.delete().where(
                parent_col == id)

            _ = session.execute(del_st)

            # put the items
            many_query = []

            if junc_table is not None:
                if not isinstance(values, list):
                    values = [values]
                many_query.append([child, values, junc_table])

            for field, values, table in many_query:
                self.process_many_query(
                    session, table, id, field, parent, values)

        except Exception:
            raise InternalServerError()

        finally:
            session.close()

        return self.get_many_one(id, parent, child)

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def patch_many_one_secure(self, id: int, parent: str, child: str, values):
        """Wrapper method for patch many method.

        Args:
            id (int): Given ID of type parent
            parent (str): Type of parent
            child (str): Type of child
            values (list or int): list of values to patch

        Return:
            function: The wrapped method.

        """
        return self.patch_many_one(id, parent, child, values)

    def patch_many_one(self, id: int, parent: str, child: str, values):
        """put data for a many to many relationship of a parent and child.

        Args:
            id (int): Given ID of type parent
            parent (str): Type of parent
            child (str): Type of child
            values (list or int): list of values to patch
        """
        try:
            session = Session()

            many_query = []
            junc_table = JuncHolder.lookup_table(parent, child)

            if junc_table is not None:
                if not isinstance(values, list):
                    values = [values]
                many_query.append([child, values, junc_table])

            for field, values, table in many_query:
                # TODO this should only insert when it doesnt already exist
                self.process_many_query(
                    session, table, id, field, parent, values)

        except Exception:
            raise InternalServerError()

        finally:
            session.close()

        return self.get_many_one(id, parent, child)

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def update_one_secure(self, id, data_model, data_resource_name,
                          table_schema, restricted_fields, request_obj, mode='PATCH'):
        """Wrapper method for update one method.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            function: The wrapped method.

        """
        return self.update_one(id, data_model, data_resource_name,
                               table_schema, restricted_fields, request_obj, mode)

    def update_one(self, id, data_model, data_resource_name,
                   table_schema, restricted_fields, request_obj, mode='PATCH'):
        """Update a single object from the data model based on it's primary key.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            dict, int: The response object and the HTTP status code.
        """
        try:
            request_obj = request_obj.json
        except Exception:
            raise NoRequestBodyFound()

        try:
            primary_key = table_schema['primaryKey']
            session = Session()
            data_obj = session.query(data_model).filter(
                getattr(data_model, primary_key) == id).first()
            if data_obj is None:
                session.close()
                raise ApiUnhandledError(
                    f"Resource with id '{id}' not found.", 404)
        except Exception:
            raise ApiUnhandledError(f"Resource with id '{id}' not found.", 404)

        _ = Schema(table_schema)
        errors = []
        accepted_fields = []
        if validate(table_schema):
            for field in table_schema['fields']:
                accepted_fields.append(field['name'])
            for field in request_obj.keys():
                if field not in accepted_fields:
                    errors.append(f"Unknown field '{field}' found.")
                elif field in restricted_fields:
                    errors.append(
                        f"Cannot update restricted field '{field}'.")
        else:
            session.close()
            raise ApiError('Data schema validation error.', 400)

        if len(errors) > 0:
            session.close()
            raise ApiError('Invalid request body.', 400, errors)

        if mode == 'PATCH':
            for key, value in request_obj.items():
                setattr(data_obj, key, value)
            session.commit()
        elif mode == 'PUT':
            for field in table_schema['fields']:
                if field['required'] and field['name'] not in request_obj.keys():
                    errors.append(
                        f"Required field '{field['name']}' is missing.")

            if len(errors) > 0:
                session.close()
                raise ApiError('Invalid request body.', 400, errors)

            for key, value in request_obj.items():
                setattr(data_obj, key, value)
            session.commit()

        session.close()
        return {'message': f"Successfully updated resource '{id}'."}, 201

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def delete_one_secure(self, id, data_resource):
        """Wrapper method for delete one method.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            function: The wrapped method.

        """
        return self.delete_one(id, data_resource)

    def delete_one(self, id, data_resource):
        """Delete a single object from the data model based on it's primary key.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            dict, int: The response object and the HTTP status code.
        """
        pass

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def delete_many_one_secure(self, id: int, parent: str, child: str, values):
        return self.delete_many_one(id, parent, child, values)

    def delete_many_one(self, id: int, parent: str, child: str, values):
        try:
            session = Session()
            junc_table = JuncHolder.lookup_table(parent, child)

            if not isinstance(values, list):
                values = [values]

            for value in values:
                parent_col = getattr(junc_table.c, f'{parent}_id')
                child_col = getattr(junc_table.c, f'{child}_id')
                del_st = junc_table.delete().where(and_(
                    parent_col == id,
                    child_col == value
                ))

                res = session.execute(del_st)
                print(res)
                session.commit()

        except Exception:
            session.rollback()
            raise InternalServerError()

        finally:
            session.close()

        return self.get_many_one(id, parent, child)
