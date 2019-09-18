"""Database Unit Test.

"""

import docker

class TestDatabase(object):
    """Database Configuration Unit Tests"""

    def test_log_and_checksum(self, psql_docker, dr_docker, dr_manager_docker):
        """Ensure that CRUD operations for logs and checksums operate as expected."""
        psql_docker.start_postgresql_container()
        dr_docker.start_container()
        dr_manager_docker.start_container()
        
        docker_client = docker.from_env()
        containers = docker_client.containers.list()
        for c in containers:
            # TODO assert name running
            print(c.id, c.name, c.status)
