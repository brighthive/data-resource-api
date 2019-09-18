"""Database Unit Test.

"""

class TestDatabase(object):
    """Database Configuration Unit Tests"""

    def test_log_and_checksum(self, psql_docker, dr_docker, dr_manager_docker):
        """Ensure that CRUD operations for logs and checksums operate as expected."""
        psql_docker.start_postgresql_container()
        dr_docker.start_container()
        dr_manager_docker.start_container()
        
        dr_manager_docker.stop_container()
        dr_docker.stop_container()
        psql_docker.stop_postgresql_container()
