"""Generic Resource Handler.

"""

import math
import re
from collections import OrderedDict
from data_resource_api.db import Session


class ResourceHandler(object):
    def build_json_from_object(self, obj: object):
        resp = {key: value for key, value in obj.__dict__.items(
        ) if not key.startswith('_') and not callable(key)}
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
        links = OrderedDict()
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

    def get_all(self, data_model, data_resource_name, offset=0, limit=1):
        session = Session()
        response = OrderedDict()
        response[data_resource_name] = []
        response['links'] = []
        try:
            results = session.query(data_model).limit(
                limit).offset(offset).all()
            for row in results:
                response[data_resource_name].append(
                    self.build_json_from_object(row))
            row_count = session.query(data_model).count()
            if row_count > 0:
                links = self.build_links(
                    data_resource_name, offset, limit, row_count)
            response['links'] = links
        except Exception as e:
            print('exception to be logged {}'.format(e))
        return response, 200
        session.close()

    def insert_one(self, data_resource):
        return {'message': 'inserted one'}, 200

    def get_one(self, id, data_model, data_resource_name):
        return {'message': 'get one {}'.format(id)}, 200

    def update_one(self, id, data_resource):
        pass

    def delete_one(self, id, data_resource):
        pass
