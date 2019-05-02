"""Application Builder

This script is the application's entrypoint. It launches the Data Resource Manager
in it's own thread and creates a Flask application.

"""

from threading import Thread
from data_resource_api import DataResourceManager
data_resource_manager = DataResourceManager()
data_resource_manager_thread = Thread(target=data_resource_manager.run, args=())
data_resource_manager_thread.start()

app = application = data_resource_manager.create_app()
