# import time module, Observer, FileSystemEventHandler
import os
import time

from data_resource_api.app.utils.config import ConfigFunctions
from data_resource_api.app.utils.db_handler import DBHandler
from data_resource_api.config import ConfigurationFactory
from data_resource_api.logging import LogFactory
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


logger = LogFactory.get_console_logger("file-watcher")


class MigrationFileWatcher:
    def __init__(self):
        self.observer = Observer()
        self.app_config = ConfigurationFactory.from_env()
        self.config = ConfigFunctions(self.app_config)
        _, self.watchDirectory = self.config.get_alembic_config()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.debug("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == "created":
            # Event is created, you can process it now
            logger.debug("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == "modified":
            # Event is modified, you can process it now
            logger.debug("Watchdog received modified event - % s." % event.src_path)

    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None

        full_file_path = event.src_path
        file_name = os.path.basename(full_file_path)
        logger.debug("Attempting to open migration file...")
        with open(full_file_path, "rb") as file_:
            logger.debug("Attempting to run save_migration function...")
            DBHandler.save_migration(file_name, file_.read())
