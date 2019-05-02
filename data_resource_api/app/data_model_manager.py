"""Data Model Manager

The Data Model Manager is responsible for managing the lifecycle of data models
for the data resource under management. It is designed to run in it's own thread,
monitoring data resources on a regular interval.

"""

from threading import Thread
from time import sleep
from data_resource_api import ConfigurationFactory


class DataModelManager(Thread):
    """Data Model Manager Class.

    This class extends the Thread base class and is intended to be run in its own thread.
    It will monitor the data resource schemas for changes and update the tables as needed.

    """

    def __init__(self):
        Thread.__init__(self)
        self.app_config = ConfigurationFactory.from_env()

    def run(self):
        while True:
            print('Data Model Manager Running...')
            sleep(self.get_sleep_interval())

    def get_sleep_interval(self):
        """Retrieve the thread's sleep interval.

        Returns:
            int: The sleep interval (in seconds) for the thread.

        Note:
            The method will look for an enviroment variable (SLEEP_INTERVAL).
            If the environment variable isn't set or cannot be parsed as an integer,
            the method returns the default interval of 30 seconds.

        """

        return self.app_config.DATA_RESOURCE_SLEEP_INTERVAL
