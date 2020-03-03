"""Pytest Fixtusres"""

import os
import pytest
import docker
from data_resource_api import ConfigurationFactory
from data_resource_api.app.data_resource_manager import DataResourceManagerSync
from data_resource_api.app.data_model_manager import DataModelManagerSync
from pathlib import Path
from time import sleep
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor,
    credentials_descriptor,
    programs_descriptor)

from sqlalchemy.ext.declarative import declarative_base
from data_resource_api.logging import LogFactory
from data_resource_api.utils import exponential_backoff
from data_resource_api.app.descriptor import Descriptor
from data_resource_api.app.junc_holder import JuncHolder

logger = LogFactory.get_console_logger('conftest')


class PostgreSQLContainer(object):
    """A PostgreSQL Container Object.

    This class provides a mechanism for managing PostgreSQL Docker containers
    so that it can be injected into unit tests.

    Class Attributes:
        config (object): A Configuration Factory object.
        container (object): The Docker container object.
        for schema_dict in schema_dicts:
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

    def start_container(self):
        """Start PostgreSQL Container."""
        self.stop_if_running()
        try:
            self.docker_client.images.pull(self.get_postgresql_image())
        except Exception as e:
            logger.error(e)

        self.container = self.docker_client.containers.run(
            self.get_postgresql_image(),
            detach=True,
            auto_remove=True,
            name=self.config.CONTAINER_NAME,
            environment=self.db_environment,
            ports=self.db_ports)

    def stop_if_running(self):
        try:
            running = self.docker_client.containers.get(self.config.CONTAINER_NAME)
            logger.info(f"Killing running container '{self.config.CONTAINER_NAME}'")
            running.stop()
        except Exception as e:
            if "404 Client Error: Not Found" in str(e):
                return
            raise e

    def stop_container(self):
        """Stop PostgreSQL Container."""
        if self.container is None:
            self.container = self.docker_client.containers.get(
                self.config.CONTAINER_NAME)

        if self.container is not None:
            self.container.stop()


def delete_migration_artifacts():
    logger.info('Deleting migration artifacts...')
    rootdir = os.path.abspath('./migrations/versions')

    for file in os.listdir(os.fsencode(rootdir)):
        filename = os.fsdecode(file)
        if filename.endswith(".py"):
            os.remove(os.path.join(rootdir, filename))
        else:
            continue


class UpgradeFail(Exception):
    pass


class Client():
    def __init__(self, schema_dicts=None):
        if schema_dicts is not None and type(schema_dicts) != list:
            schema_dicts = [schema_dicts]

        self.schema_dicts = schema_dicts

    def run_and_return_test_client(self):
        delete_migration_artifacts()

        self.initalize_objects()

        try:
            self.upgrade_loop()
            return self.app.test_client()
        except UpgradeFail:
            logger.error("Failed to upgrade database.")

    def initalize_objects(self):
        self.data_resource_manager = DataResourceManagerSync()
        self.app = self.data_resource_manager.create_app()
        self.postgres = PostgreSQLContainer()
        self.postgres.start_container()
        self.data_model_manager = DataModelManagerSync()

    def upgrade_loop(self):
        upgraded = False
        self.counter = 1
        self.counter_max = 10
        exponential_time = exponential_backoff(1, 1.5)

        while not upgraded and self.counter <= self.counter_max:
            try:
                with self.app.app_context():
                    logger.info("------------- running upgrade")
                    self.data_model_manager.initalize_base_models()

                    if self.schema_dicts is None:
                        logger.info("------------- running monitor data resources")
                        self.data_resource_manager.monitor_data_resources()
                        
                        logger.info("------------- running monitor data models")
                        self.data_model_manager.monitor_data_models()
                    else:
                        for schema_dict in self.schema_dicts:
                            desc = Descriptor(schema_dict, "schemas_loaded_into_test_fixture")

                            logger.info("------------- running monitor data resources")
                            self.data_resource_manager.process_descriptor(desc)

                            logger.info("------------- running monitor data models")                            
                            self.data_model_manager.process_descriptor(desc)

                    self.data_model_manager.initalize_base_models()
                    upgraded = True
                    return True

            except Exception as e:
                logger.error(e)

                sleep_time = exponential_time()
                logger.info(f"Not upgraded, sleeping {sleep_time} seconds... {self.counter}/{self.counter_max} time(s)")

                self.counter += 1
                sleep(sleep_time)

        if self.counter > self.counter_max:
            logger.info("Max fail reached; stopping postgres container")
            self.postgres.stop_container()
            raise UpgradeFail

    def stop_container(self):
        self.postgres.stop_container()


@pytest.fixture(scope='module')
def regular_client():
    """Setup the PostgreSQL database instance and run migrations.

    Returns:
        client (object): The Flask test client for the application.
    """
    client = Client([credentials_descriptor, programs_descriptor])
    yield client.run_and_return_test_client()
    client.stop_container()


@pytest.fixture(scope='module')
def frameworks_skills_client():
    client = Client([frameworks_descriptor, skills_descriptor])
    yield client.run_and_return_test_client()
    client.stop_container()


@pytest.fixture
def base():
    JuncHolder.reset()
    base = declarative_base()
    yield base
    del base
