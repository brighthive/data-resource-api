"""Application Builder

This script is the application's entrypoint. It launches the Data Resource Manager
in it's own thread and creates a Flask application.

"""

from data_resource_api import DataResourceManager

app = application = data_resource_manager.create_app()
