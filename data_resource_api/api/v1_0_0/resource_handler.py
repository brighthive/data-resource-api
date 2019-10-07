"""Generic Resource Handler.

"""

import math
import re
import json
from collections import OrderedDict
from tableschema import Table, Schema, validate
from brighthive_authlib import token_required
from data_resource_api import ConfigurationFactory
from data_resource_api.db import Session
from data_resource_api.db.orm_lookup import get_class_by_tablename


class ResourceHandler(object):
    def build_json_from_object(self, obj: object, restricted_fields: dict = []):
        resp = {key: str(value) if value is not None else '' for key, value in obj.__dict__.items(
        ) if not key.startswith('_') and not callable(key) and key not in restricted_fields}
        return resp

    def compute_offset(self, page, items_per_page):
        """Compute the offset value for pagination.
        Args:
            page (int): The current page to compute the offset from.
            items_per_page (int): Number of items per page.
        Returns:
            int: The offset value.
        """
        return (page - 1) * items_per_page

    def compute_page(self, offset, items_per_page):
        """Compute the current page number based on offset.
        Args:
            offset (int): The offset to use to compute the page.
            items_per_page (int): Nimber of items per page.
        Returns:
            int: The page number.
        """

        return int(math.ceil((int(offset) / int(items_per_page)))) + 1

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

    def error_message(error_text: str, status_code=400):
        """Generate an error message with a status code.
        Args:
            error_text (str): Error text to return with the message body.
            status_code (int): HTTP status code to return.
        Return
            dict, int: Error message and HTTP status code.
        """
        return {'error': error_text}, status_code

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def get_all_secure(self, data_model, data_resource_name, restricted_fields, offset=0, limit=1):
        """Wrapper method for get_all method.

        Args:
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            offset (int): Pagination offset.
            limit (int): Result limit.

        Return:
            function: The wrapped method.

        """
        return self.get_all(data_model, data_resource_name, restricted_fields, offset, limit)

    def get_all(self, data_model, data_resource_name, restricted_fields, offset=0, limit=1):
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
        except Exception as e:
            print('exception to be logged {}'.format(e))
        session.close()
        return response, 200

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def query_secure(self, data_model, data_resource_name, restricted_fields, table_schema, request_obj):
        """Wrapper method for query."""
        return self.query(data_model, data_resource_name, restricted_fields, table_schema, request_obj)

    def query(self, data_model, data_resource_name, restricted_fields, table_schema, request_obj):
        """Query the data resource."""

        try:
            request_obj = request_obj.json
        except Exception:
            return {'error': 'No request body found.'}, 400

        errors = []
        schema = Schema(table_schema)
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
                return {'message': 'Invalid request body.', 'errors': errors}, 400
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
                except Exception as e:
                    return {'error': 'Failed to create new resource.'}, 400
                finally:
                    session.close()
        else:
            return {'error': 'Data schema validation error.'}, 400

        return {'message': 'querying data resource'}, 200

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def insert_one_secure(self, data_model, data_resource_name, table_schema, request_obj):
        """Wrapper method for insert one method.

        Args:
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.
            request_obj (dict): HTTP request object.

        Return:
            function: The wrapped method.

        """
        return self.insert_one(data_model, data_resource_name, table_schema, request_obj)

    def insert_one(self, data_model, data_resource_name, table_schema, request_obj):
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
            return {'error': 'No request body found.'}, 400

        schema = Schema(table_schema)
        errors = []
        accepted_fields = []
        if validate(table_schema):
            for field in table_schema['fields']:
                accepted_fields.append(field['name'])
                if field['required']:
                    if not field['name'] in request_obj.keys():
                        errors.append(
                            'Required field \'{}\' is missing'.format(field['name']))
            for field in request_obj.keys():
                if field not in accepted_fields:
                    errors.append('Unknown field \'{}\' found'.format(field))
        else:
            return {'error': 'Data schema validation error.'}, 400

        if len(errors) > 0:
            return {'message': 'Invalid request body.', 'errors': errors}, 400
        else:
            try:
                session = Session()
                new_object = data_model()
                for key, value in request_obj.items():
                    setattr(new_object, key, value)
                session.add(new_object)
                session.commit()
                id = getattr(new_object, table_schema['primaryKey'])
                return {'message': 'Successfully added new resource.', 'id': id}, 201
            except Exception as e:
                return {'error': 'Failed to create new resource.'}, 400
            finally:
                session.close()

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
            return {'error': 'Resource with id \'{}\' not found.'.format(id)}, 404

    def get_one_many(self, id, data_model, data_resource_name, table_schema, child):
        print("^^^^^^^^one to many func^^^^^^^^^^^^^^^")
        orm = get_class_by_tablename(child + '_rel')
        print(vars(orm))
        # print(vars(data_model))
        # print(data_model[child])
        try:
            primary_key = table_schema['primaryKey']
            session = Session()
            parent = session.query(data_model, orm).filter(
                getattr(data_model, primary_key) == id).all()
            
            print("^^^^^^^^end^^^^^^^^^^^^^^^")
            response = self.build_json_from_object(parent)
            return response, 200
        except Exception as e:
            print(e)
            return {'error': 'asdf'}, 404

    @token_required(ConfigurationFactory.get_config().get_oauth2_provider())
    def update_one_secure(self, id, data_model, data_resource_name, table_schema, restricted_fields, request_obj, mode='PATCH'):
        """Wrapper method for update one method.

        Args:
            id (any): The primary key for the specific object.
            data_model (object): SQLAlchemy ORM model.
            data_resource_name (str): Name of the data resource.
            table_schema (dict): The Table Schema object to use for validation.

        Return:
            function: The wrapped method.

        """
        return self.update_one(id, data_model, data_resource_name, table_schema, restricted_fields, request_obj, mode)

    def update_one(self, id, data_model, data_resource_name, table_schema, restricted_fields, request_obj, mode='PATCH'):
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
            return {'error': 'No request body found.'}, 400

        try:
            primary_key = table_schema['primaryKey']
            session = Session()
            data_obj = session.query(data_model).filter(
                getattr(data_model, primary_key) == id).first()
            if data_obj is None:
                return {'error': 'Resource with id \'{}\' not found.'.format(id)}, 404
        except Exception as e:
            return {'error': 'Resource with id \'{}\' not found.'.format(id)}, 404

        schema = Schema(table_schema)
        errors = []
        accepted_fields = []
        if validate(table_schema):
            for field in table_schema['fields']:
                accepted_fields.append(field['name'])
            for field in request_obj.keys():
                if field not in accepted_fields:
                    errors.append('Unknown field \'{}\' found'.format(field))
                elif field in restricted_fields:
                    errors.append(
                        'Cannot update restricted field \'{}\''.format(field))
        else:
            return {'error': 'Data schema validation error.'}, 400

        if len(errors) > 0:
            return {'message': 'Invalid request body.', 'errors': errors}, 400
        else:
            if mode == 'PATCH':
                for key, value in request_obj.items():
                    setattr(data_obj, key, value)
                session.commit()
            elif mode == 'PUT':
                for field in table_schema['fields']:
                    if field['required'] and field['name'] not in request_obj.keys():
                        errors.append('Required field \'{}\' is missing'.format(field['name']))
                if len(errors) > 0:
                    return {'message': 'Invalid request body.', 'errors': errors}, 400
                for key, value in request_obj.items():
                    setattr(data_obj, key, value)
                session.commit()
            return {'message': 'Successfully updated resource \'{}\''.format(id)}, 201

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
