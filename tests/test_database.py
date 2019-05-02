"""Database Unit Test.

"""

from data_resource_api import Session, Checksum, Log


class TestDatabase(object):
    """Database Configuration Unit Tests"""

    def test_log_and_checksum(self, psql_docker):
        """Ensure that CRUD operations for logs and checksums operate as expected."""
        psql_docker.start_postgresql_container()
        psql_docker.stop_postgresql_container()
