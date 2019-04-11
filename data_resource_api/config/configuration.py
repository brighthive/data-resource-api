"""Application Configuration Objects and Factory.

"""

import os
import json


class InvalidConfigurationError(Exception):
    """Invalid configuration factory object exception."""
    pass


class Config(object):
    """Base configuration class.

    Class Attributes:
        RELATIVE_PATH (str): The configuration file's relative location on disk.
        ABSOLUTE_PATH (str): The configuration file's absolute path on disk.
        ROOT_PATH (str): The application's root location on disk derived from subtracting this file's
            relative path from it's absolute path.

    """
    RELATIVE_PATH = os.path.dirname(os.path.relpath(__file__))
    ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    ROOT_PATH = ABSOLUTE_PATH.split(RELATIVE_PATH)[0]
    MIGRATION_HOME = os.getenv(
        'MIGRATION_HOME', os.path.join(ROOT_PATH, 'migrations'))
    SLEEP_INTERVAL = os.getenv('SLEEP_INTERVAL', 30)


class TestConfig(Config):
    """Unit testing configuration class.


    """

    def __init__(self):
        super().__init__()


class IntegrationTestConfig(Config):
    """Integration testing configuration class.

    """

    def __init__(self):
        super().__init__()


class DevelopmentConfig(Config):
    """Development configuration class.


    """

    def __init__(self):
        super().__init__()


class SandboxConfig(Config):
    """Sandbox deployment configuration class.

    """

    def __init__(self):
        super().__init__()


class ProductionConfig(Config):
    """Production deployment configuration class.

    """

    def __init__(self):
        super().__init__()


class ConfigurationFactory(object):
    """A factory for handling configuration object creation.

    """

    @staticmethod
    def get_config(config_type: str = 'DEVELOPMENT'):
        """ Retrieve a configuration factory based on a configuration type.

        Args:
            config_type (str): Configuration type to return factory for.
                Possible values are `TEST`, `DEVELOPMENT`, `SANDBOX`, `INTEGRATION`, and `PRODUCTION`.

        Returns:
            Config: A configuration object of the specified type.

        Raises:
            InvalidConfigurationError
        """

        config_type = config_type.upper()
        if config_type == 'TEST':
            return TestConfig()
        elif config_type == 'INTEGRATION':
            return IntegrationTestConfig()
        elif config_type == 'DEVELOPMENT':
            return DevelopmentConfig()
        elif config_type == 'SANDBOX':
            return SandboxConfig()
        elif config_type == 'PRODUCTION':
            return ProductionConfig()
        else:
            raise InvalidConfigurationError(
                'Invalid configuration type `{}` specified.'.format(config_type))

    @staticmethod
    def from_env():
        """Retrieve a configuration object from the environment.

        Notes:
            Provides a configuration object based on the `APP_ENV` environment variable. Defaults to the development
            environment if the variable is left unset.

        Returns:
            Config: Configuration object based on the configuration environment supplied in the `APP_ENV` environment variable.

        """
        return ConfigurationFactory.get_config(os.getenv('APP_ENV', 'DEVELOPMENT'))
