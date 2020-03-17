"""Data Model Manager Runner

This script is responsible for running the Data Model Manager in its own
thread, separate from the web application that will most likely have multiple
workers.

"""

from threading import Thread
from data_resource_api import DataModelManager
from data_resource_api import MigrationFileWatcher

migration_file_watcher = MigrationFileWatcher()
migration_file_watcher_thread = Thread(
    target=migration_file_watcher.run, args=()
)
migration_file_watcher_thread.start()

data_model_manager = DataModelManager()
data_model_manager_thread = Thread(target=data_model_manager.run, args=())
data_model_manager_thread.start()
