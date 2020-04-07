"""Database and ORM Fixtures."""

from data_resource_api.config import ConfigurationFactory
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


data_resource_config = ConfigurationFactory.from_env()
engine = create_engine(data_resource_config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()
