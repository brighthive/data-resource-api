import os

from alembic.config import Config
from data_resource_api.logging import LogFactory


logger = LogFactory.get_console_logger("config")


class ConfigFunctions:
    def __init__(self, app_config):
        self.app_config = app_config

    def get_sleep_interval(self):
        """Retrieve the thread's sleep interval.

        Returns:
            int: The sleep interval (in seconds) for the thread.

        Note:
            The method will look for an enviroment variable (SLEEP_INTERVAL).
            If the environment variable isn't set or cannot be parsed as an integer,
            the method returns the default interval of 30 seconds.
        """

        return self.app_config.DATA_MODEL_SLEEP_INTERVAL

    def get_data_resource_schema_path(self):
        """Retrieve the path to look for data resource specifications.

        Returns:
            str: The search path for data resource schemas.

        Note:
            The application will look for an environment variable named DATA_RESOURCE_PATH
            and if it is not found will revert to the default path (i.e. /path/to/application/schema).
        """

        return os.getenv(
            "DATA_RESOURCE_PATH", os.path.join(self.app_config.ROOT_PATH, "schema")
        )

    def get_alembic_config(self):
        """Load the Alembic configuration.

        Returns:
            object, object: The Alembic configuration and migration directory.
        """

        try:
            alembic_config = Config(
                os.path.join(self.app_config.ROOT_PATH, "alembic.ini")
            )
            migrations_dir = os.path.join(
                self.app_config.ROOT_PATH, "migrations", "versions"
            )
            if not os.path.exists(migrations_dir) or not os.path.isdir(migrations_dir):
                migrations_dir = None
            return alembic_config, migrations_dir
        except Exception:
            logger.exception("Error loading alembic config")
            return None, None
