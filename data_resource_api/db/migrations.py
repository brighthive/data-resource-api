"""This stores migraiton files.

It allows the application to save and load migration files to restore
the state of the application.
"""

from data_resource_api.db import Base
from sqlalchemy import Column, LargeBinary, String


class Migrations(Base):
    __tablename__ = "migrations"
    file_name = Column(String, primary_key=True)
    file_blob = Column(LargeBinary, nullable=False)
