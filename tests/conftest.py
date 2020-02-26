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
            print('Exception {}'.format(e))

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
            print(f"Killing running container '{self.config.CONTAINER_NAME}'")
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
    print('Deleting migration artifacts...')
    rootdir = os.path.abspath('./migrations/versions')

    for file in os.listdir(os.fsencode(rootdir)):
        filename = os.fsdecode(file)
        if filename.endswith(".py"):
            os.remove(os.path.join(rootdir, filename))
        else:
            continue


class UpgradeFail(Exception): pass


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
            print("Failed to upgrade database.")

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
        while not upgraded and self.counter <= self.counter_max:
            try:
                with self.app.app_context():
                    print("------------- running upgrade")
                    self.data_model_manager.initalize_base_models()

                    if self.schema_dicts is None:
                        print("------------- running monitor data resources")
                        self.data_resource_manager.monitor_data_resources()
                        print("------------- running monitor data models")
                        self.data_model_manager.monitor_data_models()
                    else:
                        for schema_dict in self.schema_dicts:
                            print("------------- running monitor data resources")
                            self.data_resource_manager.work_on_schema(schema_dict, "schemas_loaded_into_test_fixture")
                            print("------------- running monitor data models")
                            self.data_model_manager.work_on_schema(schema_dict, "schemas_loaded_into_test_fixture")
                    
                    self.data_model_manager.initalize_base_models()
                    upgraded = True
                    return True

            except Exception as e:
                print(f"Not upgraded, sleeping... {self.counter}/{self.counter_max} time(s)")
                self.counter += 1
                sleep(1)
        
        if self.counter > self.counter_max:
            print("Max fail reached; stopping postgres container")
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


# @pytest.fixture(scope='module')
# def test_client():
#     client = Client(custom_descriptor)
#     yield client.run_and_return_test_client()
#     client.stop_container()
