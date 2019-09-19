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
        if self.container: return

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


class DataResourceContainer():
    def __init__(self, manager=False):
        self.config = ConfigurationFactory.get_config('TEST')
        self.container = None
        self.manager = manager
        self.docker_client = docker.from_env()

        if self.manager:
            self.command = self.config.DATA_RESOURCE_MANAGER_COMMAND
            self.name = self.config.DATA_RESOURCE_CONTAINER_NAME + '_manager'
            self.db_ports = None
        
        else:
            self.command = self.config.DATA_RESOURCE_MANAGER_COMMAND
            self.name = self.config.DATA_RESOURCE_CONTAINER_NAME
            self.db_ports = {8000:8000}
            
        self.environment = [
            'APP_ENV=SANDBOX',
            'POSTGRES_USER=test_user',
            'POSTGRES_PASSWORD=test_password',
            'POSTGRES_DATABASE=data_resource_dev',
            'POSTGRES_HOSTNAME=postgres',
            'POSTGRES_PORT=5432'
            # 'POSTGRES_USER={}'.format(self.config.POSTGRES_USER),
            # 'POSTGRES_PASSWORD={}'.format(self.config.POSTGRES_PASSWORD),
            # 'POSTGRES_DB={}'.format(self.config.POSTGRES_DATABASE),
            # 'POSTGRES_PORT=5432',
            # 'POSTGRES_DATABASE=data_resource_dev',
            # 'POSTGRES_HOSTNAME=postgres'
        ]

    def get_image(self):
        """Output the DataResourceManager image from the configuation.

        Returns:
            str: The DataResourceManager image name and version tag.
        """
        return f'{self.config.DATA_RESOURCE_IMAGE}' \
            f':{self.config.DATA_RESOURCE_VERSION}'

    def start_container(self):
        if self.container: return

        try:
            self.docker_client.images.pull(self.get_image())
        except Exception as e:
            print(f'Exception {e}')

        full_volume_path = os.path.abspath('./schema')

        self.container = self.docker_client.containers.run(
            self.get_image(),
            detach=True,
            auto_remove=True,
            name=self.name,
            environment=self.environment,
            ports=self.db_ports,
            command=self.command,
            volumes={
                full_volume_path: {
                    'bind': '/data-resource-schema',
                    'mode': 'rw'
                }
            }
        )

    def stop_container(self):
        if self.container is None:
            self.container = self.docker_client.containers.get(
                self.name
            )
        
        self.container.stop()
        
    def wait_for_ready(self):
        if not self.manager: return

        # check logs until we are ready
        counter = 0
        for log in self.container.logs(stream=True):
            counter += 1
            print(log)

            if counter >= 15:
                print("Message cap reached, returning...")
                return

            # if "Sleeping for 60 seconds".encode() in log: return
            if "Context impl PostgresqlImpl".encode() in log:
                return

        # print(self.container.logs(stream=True))
        # self.container.logs(since=datetime)
        # self.container.logs(follow=True)
        # while True:
        # print(self.container.logs())


@pytest.fixture(scope='module')
def psql_docker():
    """Database container."""
    container = PostgreSQLContainer()
    yield container
    container.stop_postgresql_container()


@pytest.fixture(scope='module')
def dr_docker():
    """Database container."""
    container = DataResourceContainer()
    yield container
    container.stop_container()


@pytest.fixture(scope='module')
def dr_manager_docker():
    """Database container."""
    container = DataResourceContainer(True)
    yield container
    container.stop_container()
