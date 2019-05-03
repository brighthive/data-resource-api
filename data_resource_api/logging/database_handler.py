"""Log Handler for Database Logging.

"""

import traceback
from logging import Handler
from data_resource_api.db import Session
from data_resource_api.db.log import Log


class DatabaseHandler(Handler):
    """Database Log Handler.

    This class extends the logging handler base class to create a new log
    handler that writes to the database.

    """

    def emit(self, record):
        session = Session()
        trace = None
        exc = record.__dict__['exc_info']
        if exc:
            trace = traceback.format_exc()
        log = Log(
            logger=record.__dict__['name'],
            level=record.__dict__['levelname'],
            trace=trace,
            msg=record.__dict__['msg'],)
        session.add(log)
        session.commit()
        session.close()
