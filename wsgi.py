"""Application Builder

This script is the application's entrypoint. It launches the Data Resource Manager
in it's own thread and creates a Flask application.

"""

import threading
from time import sleep
from data_resource_api import DataResourceManager

manager = DataResourceManager()
thread = threading.Thread(target=manager.run, args=())
thread.start()
app = application = manager.create_app()
