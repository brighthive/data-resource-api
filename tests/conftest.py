"""Pytest Fixtures"""

import os
import pytest
import docker
from data_resource_api import ConfigurationFactory


class PostgreSQLContainer(object):
    """A PostgreSQL Container Object.

    This class provides a mechanism for managing PostgreSQL Docker containers
    so that it can be injected into unit tests.

    Class Attributes:
        config (object): A Configuration Factory object.
        container (object): The Docker container object.
        docker_client (object): Docker client.
        db_environment (list): Database environment configuration variables.
        db_ports (dict): Dictionary of database port mappings.

    """

    def __init__(self):
        self.config = ConfigurationFactory.get_config('TEST')
        self.container = None
        self.docker_client = docker.from_env()
        self.db_environment = [
            'POSTGRES_USER={}'.format(self.config.POSTGRES_USER),
            'POSTGRES_PASSWORD={}'.format(self.config.POSTGRES_PASSWORD),
            'POSTGRES_DB={}'.format(self.config.POSTGRES_DATABASE)
        ]
        self.db_ports = {'5432/tcp': self.config.POSTGRES_PORT}

    def get_postgresql_image(self):
        """Output the PostgreSQL image from the configuation.

        Returns:
            str: The PostgreSQL image name and version tag.
        """
        return '{}:{}'.format(self.config.IMAGE_NAME, self.config.IMAGE_VERSION)

    def start_postgresql_container(self):
        """Start PostgreSQL Container."""
        try:
            self.docker_client.images.pull(self.get_postgresql_image())
        except Exception as e:
            print('Exception {}'.format(e))

        self.container = self.docker_client.containers.run(
            self.get_postgresql_image(),
            detach=True,
            auto_remove=True,
            name=self.config.CONTAINER_NAME,
            environment=self.db_environment,
            ports=self.db_ports)

    def stop_postgresql_container(self):
        """Stop PostgreSQL Container."""
        if self.container is None:
            self.container = self.docker_client.containers.get(
                self.config.CONTAINER_NAME)
        self.container.stop()


@pytest.fixture(scope='module')
def psql_docker():
    """Database container."""
    return PostgreSQLContainer()
