"""Database and ORM Fixtures.

"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from data_resource_api.config import ConfigurationFactory
from data_resource_api.logging import LogFactory

logger = LogFactory.get_console_logger("base")


data_resource_config = ConfigurationFactory.from_env()
logger.info("Connecting to ", data_resource_config.SQLALCHEMY_DATABASE_URI)
engine = create_engine(data_resource_config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()
