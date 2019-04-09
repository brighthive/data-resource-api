"""Database and ORM Fixtures.

"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'postgresql+psycopg2://test_user:test_password@localhost:5432/data_resource_dev')
Session = sessionmaker(bind=engine)
Base = declarative_base()
