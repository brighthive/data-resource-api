"""Application Builder

"""

import threading
from time import sleep
from data_resource_api import DataResourceManager

manager = DataResourceManager()
thread = threading.Thread(target=manager.run, args=())
thread.start()
app = application = manager.create_app()
