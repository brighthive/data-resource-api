"""Pytest Fixtusres"""

import os
import pytest
import docker
from data_resource_api.config import ConfigurationFactory
from data_resource_api.app.data_managers.data_resource_manager import DataResourceManagerSync
from data_resource_api.app.data_managers.data_model_manager import DataModelManagerSync
from time import sleep
from tests.schemas import (
    frameworks_descriptor,
    skills_descriptor,
    credentials_descriptor,
    programs_descriptor,
    json_descriptor,
    everything_descriptor)

from sqlalchemy.ext.declarative import declarative_base
from data_resource_api.logging import LogFactory
from data_resource_api.utils import exponential_backoff
from data_resource_api.app.utils.junc_holder import JuncHolder

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
        return '{}:{}'.format(self.config.IMAGE_NAME,
                              self.config.IMAGE_VERSION)

    def start_container(self):
        """Start PostgreSQL Container."""
        if os.getenv('DR_LEAVE_DB', False):
            return

        if self.get_db_if_running():
            return

        try:
            self.docker_client.images.pull(self.get_postgresql_image())
        except Exception:
            logger.exception('Failed to pull postgres image')

        self.container = self.docker_client.containers.run(
            self.get_postgresql_image(),
            detach=True,
            auto_remove=True,
            name=self.config.CONTAINER_NAME,
            environment=self.db_environment,
            ports=self.db_ports)

    def stop_if_running(self):
        if os.getenv('DR_LEAVE_DB', False):
            return

        try:
            running = self.docker_client.containers.get(
                self.config.CONTAINER_NAME)
            logger.info(
                f"Killing running container '{self.config.CONTAINER_NAME}'")
            running.stop()
        except Exception as e:
            if "404 Client Error: Not Found" in str(e):
                return
            raise e

    def get_db_if_running(self):
        """Returns None or the db
        """
        if os.getenv('DR_LEAVE_DB', False):
            return

        try:
            return self.docker_client.containers.get(
                self.config.CONTAINER_NAME)
        except Exception as e:
            if "404 Client Error: Not Found" in str(e):
                return


@pytest.fixture(scope='session', autouse=True)
def run_the_database(autouse=True):
    postgres = PostgreSQLContainer()
    yield postgres.start_container()
    postgres.stop_if_running()


def delete_migration_artifacts():
    logger.info('Deleting migration artifacts...')
    rootdir = os.path.abspath('./migrations/versions')

    for file in os.listdir(os.fsencode(rootdir)):
        filename = os.fsdecode(file)
        if "000000000000_create_table_checksum_and_logs.py" in filename:
            continue

        if filename.endswith(".py"):
            os.remove(os.path.join(rootdir, filename))
        else:
            continue


class UpgradeFail(Exception):
    pass


class Client():
    def __init__(self, schema_dicts=None):
        if schema_dicts is not None and not isinstance(schema_dicts, list):
            schema_dicts = [schema_dicts]

        self.schema_dicts = schema_dicts

        if len(self.schema_dicts) == 0:
            raise RuntimeError("Need at least one schema dict for test client")

    def start(self):
        delete_migration_artifacts()

        self.initialize_test_client()

        try:
            self.upgrade_loop()
        except UpgradeFail:
            logger.exception("Failed to upgrade database.")

    def get_test_client(self):
        return self.app.test_client()

    def initialize_test_client(self):
        self.data_resource_manager = DataResourceManagerSync(
            use_local_dirs=False,
            descriptors=self.schema_dicts)
        self.app = self.data_resource_manager.create_app()
        # self.postgres = PostgreSQLContainer()
        # try:
            # self.postgres.start_container()
        # except:
        #     logger.exception('could not start database?')

        self.data_model_manager = DataModelManagerSync(
            use_local_dirs=False,
            descriptors=self.schema_dicts)

    def upgrade_loop(self):
        upgraded = False
        self.counter = 1
        self.counter_max = 10
        exponential_time = exponential_backoff(.1, 1.05)

        while not upgraded and self.counter <= self.counter_max:
            try:
                with self.app.app_context():
                    logger.info("------------- running upgrade")
                    self.data_model_manager.run(True)
                    self.data_resource_manager.run(True)
                    upgraded = True
                    return True

            except Exception:
                logger.exception('Failed to upgrade client')

                sleep_time = exponential_time()
                logger.info(
                    f"Not upgraded, sleeping {sleep_time} seconds... {self.counter}/{self.counter_max} time(s)")

                self.counter += 1
                sleep(sleep_time)

        if self.counter > self.counter_max:
            logger.info("Max fail reached; stopping postgres container")
            # self.postgres.stop_container()
            raise UpgradeFail

    def clear_database(self):
        import contextlib
        from data_resource_api.db.base import Base, engine
        # from sqlalchemy import MetaData

        # meta = MetaData()

        with contextlib.closing(engine.connect()) as con:
            trans = con.begin()
            for table in reversed(Base.metadata.sorted_tables):
                con.execute(table.delete())
            trans.commit()

    def stop_container(self):
        from data_resource_api.db.base import Base, engine
        delete_migration_artifacts()
        Base.metadata.drop_all(engine)
        with engine.connect() as con:
            con.execute('DROP TABLE alembic_version')
        # self.postgres.stop_container()


def setup_client(descriptors: list):
    client = Client(descriptors)
    client.start()
    yield client
    client.stop_container()


def clear_db_and_get_test_client(client):
    client.clear_database()
    yield client.get_test_client()


@pytest.fixture(scope='module')
def _regular_client():
    """Setup the PostgreSQL database instance and run migrations.

    Returns:
        client (object): The Flask test client for the application.
    """
    yield from setup_client([credentials_descriptor, programs_descriptor])


@pytest.fixture(scope='function')
def regular_client(_regular_client):
    yield from clear_db_and_get_test_client(_regular_client)


@pytest.fixture(scope='module')
def _frameworks_skills_client():
    yield from setup_client([frameworks_descriptor, skills_descriptor])


@pytest.fixture(scope='function')
def frameworks_skills_client(_frameworks_skills_client):
    yield from clear_db_and_get_test_client(_frameworks_skills_client)


@pytest.fixture(scope='module')
def _json_client():
    yield from setup_client([json_descriptor])


@pytest.fixture(scope='function')
def json_client(_json_client):
    yield from clear_db_and_get_test_client(_json_client)


@pytest.fixture(scope='module')
def _everything_client():
    yield from setup_client([everything_descriptor])


@pytest.fixture(scope='function')
def everything_client(_everything_client):
    yield from clear_db_and_get_test_client(_everything_client)


@pytest.fixture
def base():
    JuncHolder.reset()
    base = declarative_base()
    yield base
    del base
