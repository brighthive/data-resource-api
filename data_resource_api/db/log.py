"""Log Table."""

from data_resource_api.db import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class Log(Base):
    """Log.

    This class represents a log entry managed by the database.

    Class Attributes:
        logger (object): Name of the logger.
        level (object): Log level.
        trace (object): Full traceback printout.
        msg (object): Custom log message.
        created_at (object): Date and time the log entry was made.
    """

    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    logger = Column(String)
    level = Column(String)
    trace = Column(String)
    msg = Column(String)
    created_at = Column(DateTime, default=func.now())

    def __init__(self, logger=None, level=None, trace=None, msg=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.msg = msg

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: {} - {}>".format(
            self.created_at.strftime("%m/%d/%Y-%H:%M:%S"), self.msg[:50]
        )
